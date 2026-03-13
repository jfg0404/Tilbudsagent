import json
import re
from typing import Optional
from bs4 import BeautifulSoup


def load_products(path: str = "data/products.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_price(text: str) -> Optional[float]:
    if not text:
        return None

    txt = (
        text.replace("\xa0", " ")
        .replace("DKK", "")
        .replace("kr.", "")
        .replace("kr", "")
        .replace(",-", "")
        .strip()
    )

    match = re.findall(r"[\d\.,]+", txt)
    if not match:
        return None

    value = match[0]

    # DK format: 1.999,95 -> 1999.95
    if "." in value and "," in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    else:
        # 1.999 -> 1999
        if value.count(".") >= 1 and len(value.split(".")[-1]) == 3:
            value = value.replace(".", "")

    try:
        return float(value)
    except ValueError:
        return None


def try_json_ld_price(soup: BeautifulSoup) -> Optional[float]:
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        text = script.string or script.get_text()
        if not text:
            continue

        # crude but pragmatic scan
        patterns = [
            r'"price"\s*:\s*"([^"]+)"',
            r'"price"\s*:\s*([0-9\.,]+)'
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                price = clean_price(m.group(1))
                if price:
                    return price
    return None


def try_meta_price(soup: BeautifulSoup) -> Optional[float]:
    selectors = [
        ('meta[property="product:price:amount"]', "content"),
        ('meta[property="og:price:amount"]', "content"),
        ('meta[itemprop="price"]', "content"),
        ('span[itemprop="price"]', None),
    ]

    for selector, attr in selectors:
        el = soup.select_one(selector)
        if el:
            raw = el.get(attr) if attr else el.get_text(" ", strip=True)
            price = clean_price(raw)
            if price:
                return price
    return None


def try_custom_selector(soup: BeautifulSoup, selector: Optional[str]) -> Optional[float]:
    if not selector:
        return None

    el = soup.select_one(selector)
    if not el:
        return None

    raw = el.get("content") or el.get_text(" ", strip=True)
    return clean_price(raw)


def extract_price(html: str, selector: Optional[str] = None) -> Optional[float]:
    soup = BeautifulSoup(html, "lxml")

    for fn in [
        lambda: try_custom_selector(soup, selector),
        lambda: try_meta_price(soup),
        lambda: try_json_ld_price(soup),
    ]:
        price = fn()
        if price:
            return price

    return None
