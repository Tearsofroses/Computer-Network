from fastapi import FastAPI
import uvicorn
from .store import InMemoryStore
from .services import TrackerService
from .api import init_router