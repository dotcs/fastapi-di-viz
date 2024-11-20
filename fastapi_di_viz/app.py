import argparse

from fastapi_di_viz.utils import build_dependency_graph, mermaid_from_dot

def run(args: argparse.Namespace):
    # sanity check the app argument
    if args.app.count(":") != 1:
        raise ValueError("App argument must be in the form module_name:app_name")
    module_name, app_name = args.app.split(":")

    # Check if the module and app exist
    try:
        module = __import__(module_name, fromlist=[app_name])
    except ModuleNotFoundError:
        raise ValueError(f"Module {module_name} not found")
    try:
        app = getattr(module, app_name)
    except AttributeError:
        raise ValueError(f"App {app_name} not found in module {module_name}")

    # Build the dependency graph and convert it to the desired format
    dot = build_dependency_graph(app)
    if args.format == "dot":
        print(dot.source)
    elif args.format == "mermaid":
        print(mermaid_from_dot(dot))


def main():
    argparser = argparse.ArgumentParser(
        description="Inspect FastAPI application DI injected dependencies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argparser.add_argument(
        "app", type=str, help="FastAPI application to inspect, e.g., myapp.main:app"
    )
    argparser.add_argument(
        "--format",
        type=str,
        choices=["mermaid", "dot"],
        default="mermaid",
        help="Output format (mermaid, dot)",
    )
    args = argparser.parse_args()
    run(args)
