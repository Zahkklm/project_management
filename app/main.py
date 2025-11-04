from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, documents, invitations, join, projects
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://d2sicjv5uods5w.cloudfront.net",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(projects.router, tags=["projects"])
app.include_router(documents.router, tags=["documents"])
app.include_router(invitations.router, tags=["invitations"])
app.include_router(join.router, tags=["join"])


@app.get("/")
def root():
    return {"message": "Project Management API", "version": settings.VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
