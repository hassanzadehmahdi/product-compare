from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ---------- Input Schemas ----------

class ProductMessage(BaseModel):
    sent_at: datetime
    text: str
    sender_type: Literal["human", "bot"]
    sender_side: Literal["buyer", "seller"]


class Price(BaseModel):
    value: int  # e.g., 35000000 (in Toman or Rial)


class ProductData(BaseModel):
    title: str
    price: Price
    status: Optional[str] = "unknown"
    ram_memory: Optional[str] = None
    internal_storage: Optional[str] = None
    description: Optional[str] = None
    messages: Optional[List[ProductMessage]] = []


class ProductPost(BaseModel):
    id: str
    data: ProductData


class ComparisonRequest(BaseModel):
    posts: List[ProductPost]
    params: List[str] = Field(..., description="List of features to compare, e.g., ['حافظه داخلی', 'عمر باتری']")


# ---------- Output Schemas ----------

class ProductComparisonDetail(BaseModel):
    id: str
    description: str
    features: List[str]
    pros: List[str]
    cons: List[str]
    rate: float  # 0 to 10


class RecommendationResult(BaseModel):
    id: str
    reason: str


class ComparisonResponse(BaseModel):
    comparison_details: List[ProductComparisonDetail]
    overall_description: str
    recommendation: RecommendationResult
