import requests
from app.utils import load_products, extract_price
from app.db import (
    ensure_schema,
    upsert_product_record,
    get_product_by_url,
    insert_price_history,
    get_latest_price,
    has_alert_been_sent,
    log_alert,
)
from alerts.telegram import send_telegram_message


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def check_product(product: dict):
    print(f"Tjekker: {product['name']}")
    upsert_product_record(product)
    db_product = get_product_by_url(product["url"])
    if not db_product:
        raise ValueError("Produkt kunne ikke upsertes i DB")

    previous = get_latest_price(db_product["id"])
    previous_price = float(previous["price"]) if previous else None

    html = fetch_html(product["url"])
    price = extract_price(html, selector=product.get("price_selector"))

    if price is None:
        raise ValueError("Kunne ikke finde pris på siden")

    insert_price_history(db_product["id"], price, availability=None)

    reasons = []
    if price <= float(product["target_price"]):
        reasons.append("target_reached")
    if previous_price is not None and price < previous_price:
        reasons.append("price_drop")

    for reason in reasons:
        if not has_alert_been_sent(db_product["id"], price, reason):
            message = (
                f"Deal alert\n\n"
                f"{product['name']}\n"
                f"Butik: {product['store']}\n"
                f"Pris: {price:.2f} {product.get('currency', 'DKK')}\n"
                f"Target: {float(product['target_price']):.2f} {product.get('currency', 'DKK')}\n"
                f"Årsag: {reason}\n"
                f"URL: {product['url']}"
            )
            send_telegram_message(message)
            log_alert(db_product["id"], price, reason)

    print(f"OK: {product['name']} -> {price}")


def main():
    ensure_schema()
    products = load_products()

    active_products = [p for p in products if p.get("active", True)]
    for product in active_products:
        try:
            check_product(product)
        except Exception as e:
            print(f"FEJL på {product['name']}: {e}")


if __name__ == "__main__":
    main()
