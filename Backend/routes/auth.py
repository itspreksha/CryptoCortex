from fastapi import APIRouter, HTTPException, status, Depends, Request, Form
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from models import User, TokenResponse, UserCreate
from routes.token import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from routes.token import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    existing = await User.find_one(User.username == user.username)
    if existing:
        raise HTTPException(400, detail="Email already registered")  

    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, password_hash=hashed_password)
    await new_user.insert()

    access_token = create_access_token(data={"sub": str(new_user.id)})
    return TokenResponse(access_token=access_token)


# -----------------------------
# Login (JSON body or Form)
# -----------------------------
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    username: str = Form(None),
    password: str = Form(None)
):
    
    if username and password:
        pass 
    else:
        
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

    if not username or not password:
        return JSONResponse(status_code=422, content={"detail": "Username and password required"})

    user = await User.find_one(User.username == username)
    if not user or not pwd_context.verify(password, user.password_hash):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    access_token = create_access_token(data={"sub": str(user.id)})
 


    return TokenResponse(access_token=access_token)

