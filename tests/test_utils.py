import pytest
from typing import Annotated, Generator
from fastapi import FastAPI, Depends

from fastapi_di_viz.utils import build_dependency_graph, mermaid_from_dot

@pytest.fixture
def app_with_multiple_deps() -> Generator[FastAPI, None, None]:
    """
    A FastAPI app with a single endpoint with a single dependency.
    """
    app = FastAPI()

    class Settings: ...
    class Service: ...

    def get_settings():
        return Settings()

    # Use old syntax for dependency injection for testing purposes
    def get_service(settings = Depends(get_settings)):
        return Service()

    @app.get("/")
    def home(service: Annotated[Service, Depends(get_service)], settings: Annotated[Settings, Depends(get_settings)]):
        return {"message": "Hello, World!"}

    yield app

@pytest.fixture
def app_from_sample_app() -> Generator[FastAPI, None, None]:
    """
    A FastAPI app with the sample app from the sample module.
    This app has multiple endpoints and dependencies.
    """
    from fastapi_di_viz.sample.app import app
    yield app

def test_build_dependency_graph_empty_app():
    app = FastAPI()
    dot = build_dependency_graph(app)
    assert dot.source.strip() == "// FastAPI Dependency Graph\ndigraph {\n}"

def test_build_dependency_graph_single_route(snapshot, app_with_multiple_deps: FastAPI):
    dot = build_dependency_graph(app_with_multiple_deps)
    snapshot.assert_match(dot.source, "build_dependency_graph_single_route")

def test_build_dependency_graph_sample_app(snapshot, app_from_sample_app: FastAPI):
    dot = build_dependency_graph(app_from_sample_app)
    snapshot.assert_match(dot.source, "build_dependency_graph_sample_app")

def test_mermaid_from_dot_sample_app(snapshot, app_from_sample_app: FastAPI):
    dot = build_dependency_graph(app_from_sample_app)
    mermaid = mermaid_from_dot(dot)
    snapshot.assert_match(mermaid, "mermaid_from_dot_sample_app")
