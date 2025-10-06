# export_lb_ids_titles.py
# pip install requests
# Python 3.8+

import requests
import json
from pathlib import Path

API_LEADERBOARDS_URL = "https://retroachievements.org/API/API_GetUserGameLeaderboards.php"
TIMEOUT_SECONDS = 10

def export_ids_titles(game_id: int, user: str, api_key: str, out_file: Path):
    """
    Ruft alle Leaderboards eines Spiels ab und schreibt pro Zeile:
    <ID>\t<Title>
    """
    params = {"u": user, "y": api_key, "i": game_id}   # 'i' wie von dir gewünscht
    try:
        r = requests.get(API_LEADERBOARDS_URL, params=params, timeout=TIMEOUT_SECONDS)
        r.raise_for_status()
    except Exception as e:
        print("Fehler beim Abrufen der Leaderboards:", e)
        return False

    try:
        data = r.json()
    except Exception as e:
        print("Fehler beim Parsen der Antwort:", e)
        return False

    results = data.get("Results", [])
    if not results:
        print("Keine Leaderboards gefunden.")
        out_file.write_text("", encoding="utf-8")
        return True

    lines = []
    lines.append("ID\t: Title\n")
    
    for lb in results:
        _id = lb.get("ID", "")
        title = (lb.get("Title") or "").strip()
        # Tab-separated: ID <tab> Title
        lines.append(f"{_id}\t: {title}")

    try:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {len(lines)} entries to {out_file}")
        return True
    except Exception as e:
        print("Fehler beim Schreiben der Datei:", e)
        return False

# Beispielnutzung
if __name__ == "__main__":
    USER = "YourName"
    API_KEY = "in_settings"
    GAME_ID = 20774
    OUT = Path(r"C:\temp\game_leaderboard_titles.txt")
    export_ids_titles(GAME_ID, USER, API_KEY, OUT)
