import os
from datetime import datetime
from typing import Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Trip, Application, Guide, Review, FeedPost

app = FastAPI(title="Community Travel Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Helpers
# -------------------------

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


def serialize_list(docs: List[dict]) -> List[dict]:
    return [serialize_doc(d) for d in docs]


# -------------------------
# Health & basic routes
# -------------------------

@app.get("/")
def read_root():
    return {"message": "Community Travel Platform API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# -------------------------
# Trips
# -------------------------

@app.post("/api/trips")
def create_trip(trip: Trip):
    try:
        trip_id = create_document("trip", trip)
        return {"id": trip_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trips")
def list_trips(tag: str | None = None):
    try:
        filter_dict: dict[str, Any] = {}
        if tag:
            filter_dict["tags"] = {"$in": [tag]}
        docs = get_documents("trip", filter_dict, limit=100)
        return serialize_list(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trips/{trip_id}/apply")
def apply_to_trip(trip_id: str, application: Application):
    try:
        # Ensure trip_id ties with body
        data = application.model_dump()
        data["trip_id"] = trip_id
        app_id = create_document("application", data)
        return {"id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Guides & Reviews
# -------------------------

@app.post("/api/guides")
def create_guide(guide: Guide):
    try:
        guide_id = create_document("guide", guide)
        return {"id": guide_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/guides")
def list_guides(location: str | None = None, expertise: str | None = None):
    try:
        filter_dict: dict[str, Any] = {}
        if location:
            filter_dict["location"] = {"$regex": location, "$options": "i"}
        if expertise:
            filter_dict["expertise"] = {"$in": [expertise]}
        docs = get_documents("guide", filter_dict, limit=100)
        return serialize_list(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reviews")
def create_review(review: Review):
    try:
        review_id = create_document("review", review)
        return {"id": review_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/guides/{guide_id}/reviews")
def list_reviews_for_guide(guide_id: str):
    try:
        docs = get_documents("review", {"guide_id": guide_id}, limit=100)
        return serialize_list(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Community Feed
# -------------------------

@app.post("/api/feed")
def create_feed_post(post: FeedPost):
    try:
        post_id = create_document("feedpost", post)
        return {"id": post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feed")
def list_feed(tag: str | None = None):
    try:
        filter_dict: dict[str, Any] = {}
        if tag:
            filter_dict["tags"] = {"$in": [tag]}
        docs = get_documents("feedpost", filter_dict, limit=50)
        # Sort newest first by created_at if present
        docs.sort(key=lambda d: d.get("created_at", datetime.min), reverse=True)
        return serialize_list(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
