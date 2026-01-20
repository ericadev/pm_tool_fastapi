from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes.projects import router as projects_router
from app.routes.users import router as users_router
from app.routes.tasks import router as tasks_router

app = FastAPI()

# Configure CORS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])