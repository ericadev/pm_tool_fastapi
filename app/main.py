from fastapi import FastAPI, Depends
from app.projects import router as projects_router
from app.users import router as users_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(users_router, prefix="/users", tags=["users"])