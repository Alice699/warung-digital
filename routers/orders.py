from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from database import get_connection
from auth_utils import get_current_user

router = APIRouter()

class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    table_number: Optional[int] = None
    note: Optional[str] = None
    items: List[OrderItemIn]

@router.post("/", summary="Buat pesanan baru")
def create_order(data: OrderCreate, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    total = 0
    order_items = []

    for item in data.items:
        menu = cursor.execute(
            "SELECT * FROM menu_items WHERE id = ? AND is_available = 1", (item.menu_item_id,)
        ).fetchone()
        if not menu:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Menu ID {item.menu_item_id} tidak ditemukan.")
        subtotal = menu["price"] * item.quantity
        total += subtotal
        order_items.append((item.menu_item_id, item.quantity, subtotal))

    cursor.execute(
        "INSERT INTO orders (customer_name, table_number, note, total_price) VALUES (?, ?, ?, ?)",
        (data.customer_name, data.table_number, data.note, total)
    )
    order_id = cursor.lastrowid

    for menu_item_id, quantity, subtotal in order_items:
        cursor.execute(
            "INSERT INTO order_items (order_id, menu_item_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
            (order_id, menu_item_id, quantity, subtotal)
        )

    conn.commit()
    conn.close()
    return {"message": "Pesanan berhasil dibuat!", "order_id": order_id, "total": total}

@router.get("/", summary="Lihat semua pesanan")
def get_orders(status: Optional[str] = None, user=Depends(get_current_user)):
    conn = get_connection()
    if status:
        orders = conn.execute("SELECT * FROM orders WHERE status = ?", (status,)).fetchall()
    else:
        orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(o) for o in orders]

@router.get("/{order_id}", summary="Detail pesanan")
def get_order(order_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan.")

    items = conn.execute("""
        SELECT oi.*, mi.name, mi.price
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()
    conn.close()

    return {**dict(order), "items": [dict(i) for i in items]}

@router.patch("/{order_id}/status", summary="Update status pesanan")
def update_status(order_id: int, status: str, user=Depends(get_current_user)):
    valid = ["pending", "preparing", "ready", "done", "cancelled"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status harus salah satu dari: {valid}")
    conn = get_connection()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()
    return {"message": f"Status pesanan #{order_id} diubah ke '{status}'"}
