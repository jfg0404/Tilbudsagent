import pandas as pd
import streamlit as st
from app.db import fetch_latest_dashboard_rows, fetch_price_history

st.set_page_config(page_title="Deal Agent", layout="wide")
st.title("Deal Agent Dashboard")

rows = fetch_latest_dashboard_rows()
df = pd.DataFrame(rows)

if df.empty:
    st.info("Ingen data endnu. Kør monitor-jobbet først.")
    st.stop()

df["status"] = df.apply(
    lambda r: "UNDER TARGET"
    if pd.notnull(r["latest_price"]) and pd.notnull(r["target_price"]) and float(r["latest_price"]) <= float(r["target_price"])
    else "OVER TARGET",
    axis=1
)

st.subheader("Alle monitoreringer")
st.dataframe(
    df[["name", "product_group", "store", "latest_price", "target_price", "status", "checked_at", "url"]],
    use_container_width=True
)

st.subheader("Bedste pris pr. produktgruppe")
best = (
    df.dropna(subset=["latest_price"])
      .sort_values("latest_price", ascending=True)
      .groupby("product_group", as_index=False)
      .first()[["product_group", "name", "store", "latest_price", "target_price", "url"]]
)
st.dataframe(best, use_container_width=True)

st.subheader("Pris-historik")
name_options = df["name"].dropna().tolist()
selected_name = st.selectbox("Vælg produkt", name_options)

selected_row = df[df["name"] == selected_name].iloc[0]
history = pd.DataFrame(fetch_price_history(int(selected_row["product_id"])))

if history.empty:
    st.info("Ingen historik endnu.")
else:
    history["checked_at"] = pd.to_datetime(history["checked_at"])
    history = history.sort_values("checked_at")
    st.line_chart(history.set_index("checked_at")["price"])
