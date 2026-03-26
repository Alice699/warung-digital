from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from database import get_connection
from auth_utils import get_current_user

router = APIRouter()

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None

@router.get("/", summary="Lihat semua menu")
def get_all_menu(category: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        items = cursor.execute(
            "SELECT * FROM menu_items WHERE category = ? AND is_available = 1", (category,)
        ).fetchall()
    else:
        items = cursor.execute(
            "SELECT * FROM menu_items WHERE is_available = 1"
        ).fetchall()
    conn.close()
    return [dict(i) for i in items]

@router.get("/{item_id}", summary="Detail menu")
def get_menu_item(item_id: int):
    conn = get_connection()
    item = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan.")
    return dict(item)

@router.post("/", summary="Tambah menu baru (owner only)")
def create_menu(data: MenuItemCreate, user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Hanya owner yang bisa menambah menu.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)",
        (data.name, data.description, data.price, data.category, data.image_url)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {"message": "Menu berhasil ditambahkan!", "id": item_id}

@router.put("/{item_id}", summary="Update menu (owner only)")
def update_menu(item_id: int, data: MenuItemUpdate, user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Hanya owner yang bisa mengubah menu.")
    conn = get_connection()
    item = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan.")

    fields = {k: v for k, v in data.dict().items() if v is not None}
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE menu_items SET {set_clause} WHERE id = ?",
            (*fields.values(), item_id)
        )
        conn.commit()
    conn.close()
    return {"message": "Menu berhasil diupdate!"}

@router.delete("/{item_id}", summary="Hapus menu (owner only)")
def delete_menu(item_id: int, user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Hanya owner yang bisa menghapus menu.")
    conn = get_connection()
    conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Menu berhasil dihapus!"}
