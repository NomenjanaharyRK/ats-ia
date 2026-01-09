from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class OfferCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=5000)
    status: str = Field(default="DRAFT", pattern="^(DRAFT|PUBLISHED|ARCHIVED)$")
    
    # Nouveaux champs - tous optionnels à la création
    required_skills: Optional[List[str]] = Field(default_factory=list)
    nice_to_have_skills: Optional[List[str]] = Field(default_factory=list)
    min_experience_years: Optional[int] = Field(default=0, ge=0, le=50)
    required_education: Optional[List[str]] = Field(default_factory=list)
    required_languages: Optional[List[str]] = Field(default_factory=list)


class OfferUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, pattern="^(DRAFT|PUBLISHED|ARCHIVED)$")
    deleted: Optional[bool] = None
    
    required_skills: Optional[List[str]] = None
    nice_to_have_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = Field(None, ge=0, le=50)
    required_education: Optional[List[str]] = None
    required_languages: Optional[List[str]] = None


class OfferRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    deleted: bool = False  # ✅ DEFAULT
    owner_id: Optional[int] = None
    
    # ✅ TOUS avec defaults
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    min_experience_years: int = 0
    required_education: List[str] = Field(default_factory=list)
    required_languages: List[str] = Field(default_factory=list)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
