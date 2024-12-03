from inspect import _empty, signature
from dataclasses import dataclass
from typing import (
    Annotated,
    Callable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    get_args,
    get_origin,
)

import fastapi
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from graphviz import Digraph


@dataclass
class NodeParams:
    """Additional parameters for a node in the dependency graph."""

    is_endpoint: bool
    """
    Determines if the node is a FastAPI endpoint (entrypoint for the dependency
    injection).
    """


def get_dependencies(callable: Callable) -> List[Type]:
    """
    Get the dependencies of a callable.
    """
    sig = signature(callable)
    dependencies: List[Type] = []
    for param in sig.parameters.values():
        # Check if the parameter has an annotation (new syntax)
        if param.annotation != _empty:
            if get_origin(param.annotation) is Annotated:
                for arg in get_args(param.annotation):
                    if arg.__class__ == fastapi.params.Depends:
                        dependencies.append(arg.dependency)
            elif get_origin(param.annotation) is Depends:
                dependencies.append(param.annotation.__args__[0])

        # If not, check if the parameter has a default value (old syntax)
        else:
            if (
                param.default != _empty
                and param.default.__class__ == fastapi.params.Depends
            ):
                dependencies.append(param.default.dependency)
    return dependencies


def build_dependency_graph(app: FastAPI) -> Digraph:
    """
    Create a dependency graph of the FastAPI application as a Digraph (in DOT
    language).
    Nodes are callables and edges are dependencies.
    """
    dot = Digraph(comment="FastAPI Dependency Graph")

    visited: Set[Callable] = set()
    stack: List[Tuple[Callable, Type, NodeParams]] = []

    def visit(callable: Callable, parent: Optional[Callable] = None):
        if callable in visited:
            return
        visited.add(callable)

        dependencies = get_dependencies(callable)
        node_params = NodeParams(is_endpoint=parent is None)
        for dep in dependencies:
            stack.append((callable, dep, node_params))
            visit(dep, callable)

    for route in app.routes:
        if isinstance(route, APIRoute):
            visit(route.endpoint)

    for parent, child, params in stack:
        # Use the name of the callable if available, otherwise use the class name.
        # This is useful for lambdas and other callables without a __name__ attribute.
        child_name = getattr(child, "__name__", child.__class__.__name__)
        if params.is_endpoint:
            dot.node(parent.__name__, None, shape="rounded")
        else:
            dot.node(parent.__name__, None)
        dot.node(child_name)
        dot.edge(parent.__name__, child_name)

    return dot


def mermaid_from_dot(dot: Digraph) -> str:
    """
    Convert a Graphviz Digraph to a Mermaid diagram.
    """
    mermaid = "---\ntitle: FastAPI dependency chain\n---\n"
    mermaid += "graph TD;\n"
    for node in dot.body:
        shape = None
        if "shape" in node:
            # node content, e.g., `root [shape=rounded]`
            name = node.split("[")[0].strip()
            shape = node.split("=")[1].split("]")[0]
            if shape == "rounded":
                mermaid += f"    {name}([{name}])\n"
            else:
                mermaid += f"    {name}({name})\n"
        if "label" in node:
            name = node.split("[")[0].strip()
            label = node.split("[")[1].split("]")[0]
            mermaid += f"    {name}({label})\n"
    for edge in dot.body:
        if "->" in edge:
            source, target = edge.split("->")
            source = source.strip().split()[0]
            target = target.strip().split()[0]
            mermaid += f"    {source} --> {target}\n"
    return mermaid
