from fastapi import FastAPI

from core.config import get_settings
from routers.recommend import router as recommend_router
from routers.users import router as users_router


settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(recommend_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)