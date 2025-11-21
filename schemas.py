"""
Database Schemas for Community Travel Platform

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name (e.g., Trip -> "trip").
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date

# -------------------------
# Core Domain Schemas
# -------------------------

class Trip(BaseModel):
    title: str = Field(..., description="Short title for the trip")
    destination: str = Field(..., description="Primary destination or route")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    budget_estimate: Optional[float] = Field(None, ge=0, description="Estimated per-person budget")
    capacity: Optional[int] = Field(None, ge=1, description="Target group size")
    needed_members: Optional[int] = Field(None, ge=0, description="How many more members are needed")
    itinerary: Optional[str] = Field(None, description="Itinerary ideas / notes")
    tags: List[str] = Field(default_factory=list, description="Tags like hiking, eco, island")
    organizer_id: Optional[str] = Field(None, description="User ID of organizer")
    status: str = Field("open", description="open, planning, closed")

class Application(BaseModel):
    trip_id: str = Field(..., description="Trip reference")
    applicant_id: Optional[str] = Field(None, description="User ID of the applicant")
    message: Optional[str] = Field(None, description="Application note")
    status: str = Field("pending", description="pending, accepted, rejected")

class Guide(BaseModel):
    name: str = Field(..., description="Guide or company name")
    location: str = Field(..., description="Base location")
    expertise: List[str] = Field(default_factory=list, description="Hiking, photography, boat, etc.")
    languages: List[str] = Field(default_factory=list)
    price_per_day: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    rating: float = Field(0, ge=0, le=5)
    rating_count: int = Field(0, ge=0)

class Review(BaseModel):
    guide_id: str
    reviewer_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedPost(BaseModel):
    author_id: Optional[str] = None
    content: str = Field(..., description="Post text")
    image_url: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)
    likes: int = Field(0, ge=0)

# Note: Additional schemas like ChatRoom/Message can be added later as we expand chat features.
