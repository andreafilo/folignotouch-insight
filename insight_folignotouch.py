import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

# === CONFIGURAZIONE ===
IG_USER_ID = "17841469939432658"  # ID account Instagram
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # preso da GitHub Secrets

OUTPUT_DIR = "static"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FILE = os.path.join(OUTPUT_DIR, "insight_folignotouch_30d.csv")
PNG_FILE = os.path.join(OUTPUT_DIR, "reach_30d.png")


def fetch_json(url, params):
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def get_reach_last_30d():
    url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/insights"
    params = {
        "metric": "reach",
        "period": "day",
        "since": pd.Timestamp.today() - pd.Timedelta(days=30),
        "until": pd.Timestamp.today(),
        "access_token": ACCESS_TOKEN,
    }
    js = fetch_json(url, params)
    values = js["data"][0]["values"]
    df = pd.DataFrame(values)
    df.rename(columns={"end_time": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def get_follower_count():
    url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}"
    params = {
        "fields": "followers_count",
        "access_token": ACCESS_TOKEN,
    }
    js = fetch_json(url, params)
    return js.get("followers_count", 0)


def main():
    # --- Reach 30 giorni ---
    df = get_reach_last_30d()
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Salvato {CSV_FILE}")

    # --- Numero follower ---
    followers = get_follower_count()
    print(f"👥 Follower attuali: {followers}")

    # --- Grafico ---
    plt.figure(figsize=(12, 6))
    plt.plot(df["date"].values, df["value"].values, marker="o", color="blue", label="Reach giornaliera")
    plt.title(f"Andamento ultimi 30 giorni • @folignotouch\nFollower attuali: {followers}")
    plt.xlabel("Data")
    plt.ylabel("Reach")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(PNG_FILE)
    plt.close()
    print(f"📊 Grafico salvato in {PNG_FILE}")


if __name__ == "__main__":
    main()
