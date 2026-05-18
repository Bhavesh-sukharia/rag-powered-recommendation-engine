from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.database import init_db
from app.routes.config import router as config_router
from app.routes.movies import router as movies_router
from app.routes.recommendation import router as recommendations_router
from app.routes.users import router as users_router
from app.utils.logger import get_logger

app = FastAPI()
logger = get_logger(__name__)

# Enable CORS so preflight OPTIONS requests are handled (frontend dev)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	body = await request.body()
	try:
		request_body = body.decode("utf-8")
	except Exception:
		request_body = str(body)

	logger.warning(
		"Validation failed for %s %s: %s | body=%s",
		request.method,
		request.url.path,
		exc.errors(),
		request_body,
	)
	return JSONResponse(
		status_code=422,
		content={"detail": exc.errors()},
	)

# Include routers
app.include_router(movies_router)
app.include_router(users_router)
app.include_router(recommendations_router)
app.include_router(config_router)


@app.on_event("startup")
async def app_init():
	await init_db()


@app.get("/")
async def root():
	return {"message": "Recommendation System API Running"}
