import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .auth import router as auth_router
from .routers.users import router as users_router
from .routers.records import router as records_router
from .routers.tests import router as tests_router
from .routers.prescriptions import router as prescriptions_router
from .routers.grants import router as grants_router


def create_app() -> FastAPI:
	app = FastAPI(title=settings.app_name, debug=settings.debug)

	# CORS
	app.add_middleware(
		CORSMiddleware,
		allow_origins=[str(o) for o in settings.backend_cors_origins] or ["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	# Routers
	app.include_router(auth_router)
	app.include_router(users_router)
	app.include_router(records_router)
	app.include_router(tests_router)
	app.include_router(prescriptions_router)
	app.include_router(grants_router)

	return app


app = create_app()


def init_db():
	Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def on_startup() -> None:
	init_db()


if __name__ == "__main__":
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)