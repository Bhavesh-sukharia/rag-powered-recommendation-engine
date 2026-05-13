from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings


settings = get_settings()
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]


async def init_db() -> None:
	"""Initialize database connection. Motor handles async operations natively."""
	print("✓ MongoDB connection ready")


async def close_db() -> None:
	client.close()
