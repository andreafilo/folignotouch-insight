import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
import os
# 🔑 Inserisci il token lungo e l'ID IG
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # 👈 il token ora viene preso da un secret
IG_USER_ID   = "17841469939432658"

BASE = "https://graph.facebook.com/v23.0"

def get_reach_last_30d(ig_user_id, token):
    """Recupera la reach giornaliera ultimi 30 giorni"""
    today = datetime.now(timezone.utc).date()
    since = (today - timedelta(days=30)).isoformat()
    until = (today - timedelta(days=1)).isoformat()  # fino a ieri

    params = {
        "metric": "reach",
        "period": "day",
        "since": since,
        "until": until,
        "access_token": token
    }
    url = f"{BASE}/{ig_user_id}/insights"
    r = requests.get(url, params=params)
    r.raise_for_status()
    js = r.json()

    rows = []
    for m in js.get("data", []):
        for v in m.get("values", []):
            date = v["end_time"][:10]  # YYYY-MM-DD
            rows.append({"date": date, "reach": v["value"]})
    df = pd.DataFrame(rows).drop_duplicates(subset=["date"]).sort_values("date")
    return df

def get_followers(ig_user_id, token):
    """Recupera il numero attuale di followers"""
    url = f"{BASE}/{ig_user_id}"
    params = {"fields": "followers_count", "access_token": token}
    r = requests.get(url, params=params)
    r.raise_for_status()
    js = r.json()
    return js.get("followers_count", None)

def main():
    # 1) Reach ultimi 30 giorni
    df = get_reach_last_30d(IG_USER_ID, ACCESS_TOKEN)

    # 2) Followers totali attuali
    followers = get_followers(IG_USER_ID, ACCESS_TOKEN)

    # 3) Salvataggio CSV (reach + followers_count come riga extra)
    meta_row = pd.DataFrame([{"date": "TOTAL_followers", "reach": followers}])
    out = pd.concat([meta_row, df], ignore_index=True)
    out.to_csv("insight_folignotouch_30d.csv", index=False)
    print("✅ Salvato insight_folignotouch_30d.csv")

    # 4) Grafico
    if not df.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(df["date"], df["reach"], marker="o", label="Reach giornaliera")
        plt.title("Reach ultimi 30 giorni • @folignotouch")
        plt.xlabel("Data")
        plt.ylabel("Reach")
        plt.xticks(rotation=45, ha="right")
        plt.legend()

        # Annotazione follower totali
        if followers:
            plt.suptitle(f"Follower attuali: {followers}", y=0.97, fontsize=9)

        plt.tight_layout()
        plt.savefig("reach_30d_folignotouch.png", dpi=150)
        plt.show()
        print("✅ Grafico salvato: reach_30d_folignotouch.png")
    else:
        print("⚠️ Nessun dato reach negli ultimi 30 giorni.")

if __name__ == "__main__":
    main()
