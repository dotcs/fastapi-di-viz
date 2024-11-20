from typing import Annotated
from fastapi import FastAPI, Depends

app = FastAPI()

class Settings:
    def __init__(self):
        pass

class Repo:
    def __init__(self):
        pass

class ServiceA:
    def __init__(self, settings: Settings, repo: Repo):
        pass

class ServiceB:
    def __init__(self, repo: Repo):
        pass


def get_repo():
    return Repo()

def get_settings():
    return Settings()

def get_serviceA(repo: Annotated[Repo, Depends(get_repo)], settings: Annotated[Settings, Depends(get_settings)]):
    return ServiceA(settings, repo)

def get_serviceB(repo: Annotated[Repo, Depends(get_repo)]):
    return ServiceB(repo)

@app.get("/")
def root(settings: Annotated[Settings, Depends(get_settings)]):
    return {"message": "Hello World"}

@app.get("/a")
def a(serviceA: Annotated[ServiceA, Depends(get_serviceA)]):
    return {"message": "Hello World"}

@app.get("/b")
def b(serviceB: Annotated[ServiceB, Depends(get_serviceB)]):
    return {"message": "Hello World"}
