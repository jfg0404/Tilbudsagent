import os
from datetime import datetime, timezone
from supabase import create_client, Client


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def ensure_schema():
    # Schema oprettes i Supabase SQL editor manuelt.
    # Denne funktion er kun her for flowets skyld.
    return True


def upsert_product_record(product: dict):
    client = get_client()
    payload = {
        "name": product["name"],
        "product_group": product["product_group"],
        "store": product["store"],
        "url": product["url"],
        "target_price": product["target_price"],
        "currency": product.get("currency", "DKK"),
        "active": product.get("active", True)
    }
    client.table("products").upsert(payload, on_conflict="url").execute()


def get_product_by_url(url: str):
    client = get_client()
    res = client.table("products").select("*").eq("url", url).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def insert_price_history(product_id: int, price: float, availability: str = None):
    client = get_client()
    client.table("price_history").insert({
        "product_id": product_id,
        "price": price,
        "availability": availability,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }).execute()


def get_latest_price(product_id: int):
    client = get_client()
    res = (
        client.table("price_history")
        .select("*")
        .eq("product_id", product_id)
        .order("checked_at", desc=True)
        .limit(1)
        .execute()
    )
    data = res.data or []
    return data[0] if data else None


def has_alert_been_sent(product_id: int, price: float, reason: str) -> bool:
    client = get_client()
    res = (
        client.table("alerts_sent")
        .select("*")
        .eq("product_id", product_id)
        .eq("price", price)
        .eq("alert_reason", reason)
        .limit(1)
        .execute()
    )
    return len(res.data or []) > 0


def log_alert(product_id: int, price: float, reason: str):
    client = get_client()
    client.table("alerts_sent").insert({
        "product_id": product_id,
        "price": price,
        "alert_reason": reason,
        "sent_at": datetime.now(timezone.utc).isoformat()
    }).execute()


def fetch_latest_dashboard_rows():
    client = get_client()
    products = client.table("products").select("*").eq("active", True).execute().data or []
    rows = []

    for product in products:
        latest = (
            client.table("price_history")
            .select("*")
            .eq("product_id", product["id"])
            .order("checked_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        latest_row = latest[0] if latest else None
        rows.append({
            "product_id": product["id"],
            "name": product["name"],
            "product_group": product["product_group"],
            "store": product["store"],
            "url": product["url"],
            "target_price": product["target_price"],
            "currency": product["currency"],
            "latest_price": latest_row["price"] if latest_row else None,
            "checked_at": latest_row["checked_at"] if latest_row else None,
        })
    return rows


def fetch_price_history(product_id: int):
    client = get_client()
    res = (
        client.table("price_history")
        .select("*")
        .eq("product_id", product_id)
        .order("checked_at", desc=False)
        .execute()
    )
    return res.data or []
