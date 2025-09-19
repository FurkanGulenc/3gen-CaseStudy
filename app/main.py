from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_models

from app.api.auth.login import router as login_router  # senin login router dosyan
from app.api.auth.register import router as register_router
from app.api.auth.me import router as me_router
from app.api.auth.refresh import router as refresh_router

from app.api.projects.create_project import router as create_project_router
from app.api.projects.get_project_by_id import router as get_project_router
from app.api.projects.get_projects import router as get_projects_router
from app.api.projects.update_coords import router as update_coords_router
from app.api.projects.get_project_outputs import router as get_project_output_router

from app.api.processor.process_project import router as process_project_router
from app.api.processor.task_status import router as get_task_status_router


app = FastAPI(title="3Gen Case Study")

# CORS ayarları (frontend ile test için gerekli)
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory="media"), name="media")


@app.on_event("startup")
async def on_startup():
    await init_models()

# Ana sayfa yönlendirme
@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

# Projects sayfası
@app.get("/projects-page")
async def serve_projects_page():
    return FileResponse("frontend/projects.html")

# Project detail sayfası
@app.get("/project-detail")
async def serve_project_detail_page():
    return FileResponse("frontend/project.html")


# Routers ekle
app.include_router(login_router, prefix="/auth", tags=["auth"])
app.include_router(register_router, prefix="/auth", tags=["auth"])
app.include_router(me_router, prefix="/auth", tags=["auth"])
app.include_router(refresh_router, prefix="/auth", tags=["auth"])

app.include_router(create_project_router, prefix="/projects", tags=["Projects"])
app.include_router(get_projects_router, prefix="/projects", tags=["Projects"])
app.include_router(get_project_router, prefix="/projects", tags=["Projects"])
app.include_router(update_coords_router, prefix="/projects", tags=["Projects"])
app.include_router(get_project_output_router, prefix="/projects", tags=["Projects"])


app.include_router(process_project_router, prefix="/processor", tags=["Process"])
app.include_router(get_task_status_router, prefix="/processor", tags=["Process"])
 


# Frontend static (CSS/JS)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")