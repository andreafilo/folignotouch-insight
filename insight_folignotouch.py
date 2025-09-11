import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# === CONFIGURAZIONE ===
IG_USER_ID = "17841469939432658"  # ID account Instagram
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # preso da variabile d'ambiente GitHub
BASE = "https://graph.facebook.com/v23.0"

CSV_FILE = "static/insight_folignotouch_30d.csv"
IMG_FILE = "static/reach_30d.png"

def fetch_json(url, params):
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def get_reach_last_30d():
    since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    until = datetime.utcnow().strftime("%Y-%m-%d")

    url = f"{BASE}/{IG_USER_ID}/insights"
    params = {
        "metric": "reach",
        "period": "day",
        "since": since,
        "until": until,
        "access_token": ACCESS_TOKEN
    }
    js = fetch_json(url, params)
    values = js["data"][0]["values"]

    df = pd.DataFrame(values)
    df["date"] = pd.to_datetime(df["end_time"]).dt.strftime("%Y-%m-%d")
    df = df[["date", "value"]].rename(columns={"value": "reach"})
    return df

def get_follower_count():
    url = f"{BASE}/{IG_USER_ID}"
    params = {"fields": "followers_count", "access_token": ACCESS_TOKEN}
    js = fetch_json(url, params)
    return js.get("followers_count", 0)

def main():
    # === Ottieni dati ===
    df = get_reach_last_30d()
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Salvato {CSV_FILE}")

    followers = get_follower_count()
    print(f"👥 Follower attuali: {followers}")

    # === Grafico ===
    plt.figure(figsize=(14, 6))
    plt.plot(df["date"], df["reach"], marker="o", color="blue", label="Reach giornaliera")
    plt.grid(True, linestyle="--", alpha=0.6)

    ax = plt.gca()
    ax.set_xticks(range(len(df["date"])))
    ax.set_xticklabels(df["date"], rotation=90, fontsize=8)

    plt.title("Andamento Reach ultimi 30 giorni", fontsize=14)
    plt.xlabel("Data", fontsize=10)
    plt.ylabel("Reach", fontsize=10)

    # Riquadro follower
    ax.text(
        0.98, 0.95,
        f"Follower attuali: {followers}",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
    )

    plt.tight_layout()
    plt.savefig(IMG_FILE)
    plt.close()
    print(f"📊 Grafico salvato in {IMG_FILE}")

if __name__ == "__main__":
    main()
