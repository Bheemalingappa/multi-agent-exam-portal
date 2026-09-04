import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Organization, User
from app.api.auth import get_current_user

router = APIRouter(prefix="/organizations", tags=["Enterprise Organizations"])

class OrganizationCreateSchema(BaseModel):
    name: str
    slug: str
    max_candidates: int = 500

class OrganizationResponseSchema(BaseModel):
    id: str
    name: str
    slug: str
    max_candidates: int
    created_at: str

@router.post("", response_model=OrganizationResponseSchema, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Only platform admins can create organizations.")

    existing = db.query(Organization).filter(Organization.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Organization slug '{payload.slug}' already exists.")

    org = Organization(
        name=payload.name,
        slug=payload.slug,
        max_candidates=payload.max_candidates
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    return OrganizationResponseSchema(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        max_candidates=org.max_candidates,
        created_at=org.created_at.isoformat()
    )

@router.get("", response_model=List[OrganizationResponseSchema])
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "recruiter"]:
        raise HTTPException(status_code=403, detail="Forbidden.")

    orgs = db.query(Organization).all()
    return [
        OrganizationResponseSchema(
            id=str(o.id),
            name=o.name,
            slug=o.slug,
            max_candidates=o.max_candidates,
            created_at=o.created_at.isoformat()
        )
        for o in orgs
    ]
