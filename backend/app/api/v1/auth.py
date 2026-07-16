from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import UserInDB,UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import users_collection
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = UserInDB(
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
        role=user.role,
    )
    result = await users_collection.insert_one(user_doc.model_dump())

    return UserResponse(
        id=str(result.inserted_id),
        email=user_doc.email,
        full_name=user_doc.full_name,
        role=user_doc.role,
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    user = await users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return Token(access_token=token)

@router.get("/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "role": current_user["role"],
    }


@router.get("/admin-only")
async def admin_only_route(current_user: dict = Depends(require_role(UserRole.ADMIN))):
    return {"message": f"Welcome, admin {current_user['email']}"}