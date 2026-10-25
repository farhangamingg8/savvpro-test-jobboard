import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import applications, jobs, stats
from .core.database import Base, engine
from .core.errors import ApiError


Base.metadata.create_all(bind=engine)

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:3000,http://localhost:3001",
).split(",")

app = FastAPI(title="JobBoard Pro API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in frontend_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(part) for part in error["loc"] if part != "body"), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(stats.router)

