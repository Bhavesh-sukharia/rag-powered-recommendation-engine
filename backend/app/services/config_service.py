from typing import Dict, Any
from app.core.database import db

DEFAULT = {"cf": 50, "cb": 50, "sentimentRerank": True, "ragExplanation": True}


async def get_settings() -> Dict[str, Any]:
    configurations = db.configurations
    doc = await configurations.find_one({"_id": "settings"})
    if not doc:
        # ensure defaults exist
        await configurations.replace_one({"_id": "settings"}, DEFAULT, upsert=True)
        return dict(DEFAULT)
    # remove _id if present
    doc.pop("_id", None)
    return doc


async def get_weights() -> Dict[str, int]:
    s = await get_settings()
    return {"cf": int(s.get("cf", DEFAULT["cf"])), "cb": int(s.get("cb", DEFAULT["cb"]))}


async def set_weights(cf: int, cb: int) -> Dict[str, int]:
    await db.configurations.update_one({"_id": "settings"}, {"$set": {"cf": int(cf), "cb": int(cb)}}, upsert=True)
    return await get_weights()


async def get_options() -> Dict[str, bool]:
    s = await get_settings()
    return {"sentimentRerank": bool(s.get("sentimentRerank", DEFAULT["sentimentRerank"])), "ragExplanation": bool(s.get("ragExplanation", DEFAULT["ragExplanation"]))}


async def set_options(sentimentRerank: bool, ragExplanation: bool) -> Dict[str, bool]:
    await db.configurations.update_one({"_id": "settings"}, {"$set": {"sentimentRerank": bool(sentimentRerank), "ragExplanation": bool(ragExplanation)}}, upsert=True)
    return await get_options()
