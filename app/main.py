from fastapi import FastAPI
from app.routes.projects import router as projects_router
from app.routes.users import router as users_router
from app.routes.tasks import router as tasks_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])