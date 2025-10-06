# ra_leaderboard_obs.py
# pip install requests
# Python 3.8+

import requests, time, json
from pathlib import Path

# ====== KONFIG ======
USER = "YourName"
API_KEY = "in_settings"
OUTPUT_FILE = Path(r"C:\temp\leaderboard_display.txt")
MY_FIRSTS_FILE = Path(r"C:\temp\my_firsts.txt")
CONFIG_FILE = Path(__file__).resolve().parent / "RA_config.json"
DEFAULT_LEADERBOARD_ID = 85144
DEFAULT_GAME_ID = 20774

INTERVAL_SECONDS = 10
TIMEOUT_SECONDS = 10
COUNT = 99              # Anzahl der Einträge
COUNT_FIRSTS_INTERVAL = 30  # wie oft die #1-Zählung ausgeführt wird (Sekunden)
# ====================

API_ENTRIES_URL = "https://retroachievements.org/API/API_GetLeaderboardEntries.php"
API_LEADERBOARDS_URL = "https://retroachievements.org/API/API_GetUserGameLeaderboards.php"

def write_text(path: Path, text: str):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as e:
        print("Fehler beim Schreiben:", e)

def fetch_entries(leaderboard_id):
    params = {"i": leaderboard_id, "y": API_KEY, "c": COUNT}
    try:
        r = requests.get(API_ENTRIES_URL, params=params, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        return None, f"NETWORK_ERROR: {e}"
    if r.status_code == 401:
        return None, "401 Unauthorized: API-Key ungültig"
    if r.status_code == 404:
        return None, "404 Not Found: Prüfe Leaderboard-ID / Endpoint"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:400]}"
    try:
        return r.json(), None
    except Exception as e:
        return None, f"JSON_DECODE_ERROR: {e} - Raw: {r.text[:400]}"


def fetch_header(game_id, leaderboard_id):
    """Holt dynamisch Header-Info zum Leaderboard"""
    params = {"u": USER, "y": API_KEY, "i": game_id}  # i bleibt wie gewünscht
    try:
        r = requests.get(API_LEADERBOARDS_URL, params=params, timeout=TIMEOUT_SECONDS)
        if r.status_code != 200:
            return f"status_code: {r.status_code}\nLeaderboard {leaderboard_id}\n\nBest Time by"
        data = r.json()
        lb = next((lb for lb in data.get("Results", []) if lb.get("ID") == leaderboard_id), None)
        lb_title = lb.get("Title", "") if lb else ""
        if ")" in lb_title:
            lb_title = lb_title.replace(")", ")\n -", 1)
        return f"{lb_title}\n\nBest Time by                        "
    except Exception as e:
        print("Header Fetch Error:", e)
        return f"Leaderboard {leaderboard_id}\n\nBest Time by"


def pick_results(json_data):
    if not isinstance(json_data, dict):
        return []
    if "Results" in json_data and isinstance(json_data["Results"], list):
        return json_data["Results"]
    # fallback: rekursive Suche
    stack = [json_data]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and any(k.lower() in ("rank", "user", "score") for k in v[0].keys()):
                    return v
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(obj, list):
            for it in obj:
                if isinstance(it, (dict, list)):
                    stack.append(it)
    return []


def normalize(s): return str(s).strip().lower()


def build_text(results, header):
    parsed = []
    for e in results:
        r = e.get("Rank") or e.get("rank") or ""
        u = e.get("User") or e.get("user") or ""
        s_fmt = e.get("FormattedScore") or str(e.get("Score") or 0)
        try:
            rnum = int(r)
        except:
            rnum = None
        parsed.append({
            "rank": rnum,
            "rank_s": str(r).strip(),
            "user": str(u).strip(),
            "score": str(s_fmt).strip(),
            "raw_score": int(e.get("Score") or 0)
        })

    parsed_sorted = sorted(parsed, key=lambda x: (x["rank"] is None, x["rank"] if x["rank"] is not None else 999999))
    if not parsed_sorted:
        return "Keine Leaderboard-Daten gefunden"

    top1 = parsed_sorted[0]
    top2 = parsed_sorted[1] if len(parsed_sorted) > 1 else None

    # finde mich
    me = None
    mynorm = normalize(USER)
    for p in parsed_sorted:
        if normalize(p["user"]) == mynorm:
            me = p
            break

    def diff_str(me_score, top_score):
        if me_score is None or top_score is None:
            return ""
        diff_hund = me_score - top_score
        if diff_hund >= 0:
            prefix = "+"
            color = "🔴"  # Rot: mein Score schlechter als Top
        else:
            prefix = "-"
            color = "🟢"  # Grün: mein Score besser als Top
        total_seconds = abs(diff_hund) / 100.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{color}⏱️ {prefix}{minutes}:{seconds:05.2f}"

    # maximale Breite für die Namen ermitteln
    name_width = max(
        len(top1['user']) + 6,
        len(me['user']) + 6 if me else 0,
        len(top2['user']) + 6 if top2 else 0
    ) + 8

    if me and (me["rank"] == 1 or me["rank_s"] == "1"):
        line1 = f"1️⃣ 👤 Me:".ljust(name_width + 2) + f"{me['score']}"
        line2 = ""
        if top2:
            line2 = f"(2.) ®️ {top2['user']} (RA):".ljust(name_width) + f"{top2['score']}"
        diff_line = diff_str(me['raw_score'], top2['raw_score']) if top2 else ""
    else:
        line1 = f"1️⃣ ®️ {top1['user']} (RA):".ljust(name_width) + f"{top1['score']}"
        line2 = f"({me['rank']}.) 👤 Me:".ljust(name_width + 4) + f"{me['score']}" if me else ""
        diff_line = diff_str(me['raw_score'], top1['raw_score']) if me else ""

    return f"{header}\n{line1}\n{line2}\n\n" + "Diff to Rival:".ljust(name_width - 7) + diff_line


def count_my_firsts_for_game(game_id):
    """Zählt, in wie vielen Leaderboards des Spiels du Rank == 1 hast und gibt total zurück."""
    params = {"u": USER, "y": API_KEY, "i": game_id}  # 'i' wie in deinem Skript
    try:
        r = requests.get(API_LEADERBOARDS_URL, params=params, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        return None, None, f"NETWORK_ERROR: {e}"
    if r.status_code != 200:
        return None, None, f"HTTP {r.status_code}"
    try:
        data = r.json()
    except Exception as e:
        return None, None, f"JSON_DECODE_ERROR: {e}"
    results = data.get("Results", [])
    total = int(data.get("Total") or len(results))
    cnt = 0
    for lb in results:
        ue = lb.get("UserEntry")
        if not ue:
            continue
        try:
            rank = int(ue.get("Rank", 9999))
        except Exception:
            rank = 9999
        if rank == 1 and str(ue.get("User", "")).strip().lower() == USER.strip().lower():
            cnt += 1
    return cnt, total, None

def load_config_if_changed(last_mtime, fallback_lb, fallback_game):
    """
    Lädt die Config nur neu, wenn sie seit dem letzten Check geändert wurde.
    Gibt (leaderboard_id, game_id, new_mtime) zurück.
    """
    try:
        mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        print("Config fehlt")
        return fallback_lb, fallback_game, last_mtime  # Datei fehlt

    # Keine Änderung?
    if last_mtime == mtime:
        return fallback_lb, fallback_game, last_mtime

    try:
        with CONFIG_FILE.open(encoding="utf-8") as f:
            cfg = json.load(f)

        # Mehrstufige Unterstützung (einfach oder Leaderboards-Map)
        if isinstance(cfg.get("Leaderboards"), dict) and cfg.get("CurrentLeaderboard"):
            current = cfg.get("CurrentLeaderboard")
            lb_data = cfg.get("Leaderboards", {}).get(current, {})
            leaderboard_id = lb_data.get("LeaderboardID", cfg.get("LeaderboardID", fallback_lb))
            game_id = lb_data.get("GameID", cfg.get("GameID", fallback_game))
        else:
            leaderboard_id = cfg.get("LeaderboardID", fallback_lb)
            game_id = cfg.get("GameID", fallback_game)

        print(f"Config neu geladen: LEADERBOARD_ID={leaderboard_id}, GAME_ID={game_id}")
        return leaderboard_id, game_id, mtime

    except Exception as e:
        print("⚠️ Fehler beim Laden der Config:", e)
        return fallback_lb, fallback_game, last_mtime


def main():
    print("Starte RA Leaderboard Poller für OBS (parametrisiert)...")
    last_firsts_time = 0
    last_config_mtime = None

    # initiale Fallback IDs (falls config fehlt)
    leaderboard_id = DEFAULT_LEADERBOARD_ID
    game_id = DEFAULT_GAME_ID

    while True:
        # 🔁 Config nur neu laden, wenn sie geändert wurde
        leaderboard_id, game_id, last_config_mtime = load_config_if_changed(
            last_config_mtime, leaderboard_id, game_id
        )
            
        now = time.time()
        # Header + Entries (Hauptausgabe)
        header = fetch_header(game_id, leaderboard_id)
        json_data, err = fetch_entries(leaderboard_id)

        if err:
            write_text(OUTPUT_FILE, f"ERROR: {err} [{time.strftime('%Y-%m-%d %H:%M:%S')}]")
            print("Fetch error:", err)
        else:
            results = pick_results(json_data)
            out = build_text(results, header)
            write_text(OUTPUT_FILE, out)
            print(f"[{time.strftime('%H:%M:%S')}] leaderboard_display.txt aktualisiert.")

        # periodisch: Zähle #1 Plätze (nur alle COUNT_FIRSTS_INTERVAL Sekunden)
        if now - last_firsts_time >= COUNT_FIRSTS_INTERVAL:
            cnt, total, ferr = count_my_firsts_for_game(game_id)
            if ferr:
                write_text(MY_FIRSTS_FILE, f"ERROR: {ferr} [{time.strftime('%Y-%m-%d %H:%M:%S')}]")
                print("Count error:", ferr)
            else:
                # neue Formatierung hier:
                # sichere Prozent-Berechnung, rechtsbündige Ausrichtung und Zeitstempel
                pct = (cnt / total * 100) if total else 0.0
                width = len(str(total))        # Breite für hübsche Ausrichtung
                text = f"Top-Records on RA: {cnt:>{width+1}} / {total} · ({pct:5.1f}%)"
                write_text(MY_FIRSTS_FILE, text)

                print(f"[{time.strftime('%H:%M:%S')}] my_firsts.txt aktualisiert: {cnt} / {total}")
            last_firsts_time = now

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
