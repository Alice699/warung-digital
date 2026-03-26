from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel

from database import get_connection
from auth_utils import hash_password, verify_password, create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "cashier"  # "owner" or "cashier"

@router.post("/register", summary="Daftarkan user baru")
def register(data: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
            (data.username, hash_password(data.password), data.role)
        )
        conn.commit()
        return {"message": f"User '{data.username}' berhasil didaftarkan!"}
    except Exception:
        raise HTTPException(status_code=400, detail="Username sudah dipakai.")
    finally:
        conn.close()

@router.post("/login", summary="Login dan dapatkan token JWT")
def login(form: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE username = ?", (form.username,)
    ).fetchone()
    conn.close()

    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Username atau password salah.")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}
