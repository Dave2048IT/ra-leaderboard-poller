# RA Leaderboards — README

Kurzdoku zu den drei Dateien in diesem Ordner:

- `write_ra_leaderboards.py`  
  Der Haupt-Poller (auch im Datei-Header als `ra_leaderboard_obs.py` bezeichnet). Er fragt die RetroAchievements-API ab, baut einen OBS-freundlichen Text für das aktuelle Leaderboard und zählt periodisch, in wie vielen Leaderboards du auf Platz 1 bist. Ergebnisdateien: `leaderboard_display.txt` und `my_firsts.txt` (Standard: `C:\temp`).

- `export_leaderboard_titles.py`  
  Helfer-Script, das *alle* Leaderboards eines Spiels abruft und pro Zeile `ID\t: Title` in eine TXT-Datei schreibt (Standard: `C:\temp\game_leaderboard_titles.txt`). Nützlich, um die richtige LeaderboardID zu finden.

- `RA_config.json`  
  Einfache Konfiguration: `GameID` und `LeaderboardID`. Das Poller-Script prüft die Datei automatisch auf Änderungen (mtime) und übernimmt neue Werte ohne Neustart.

---

## Voraussetzungen

- Python 3.8+
- `requests` installieren:

```bash
pip install requests
```

- Internetzugang (RetroAchievements API)
- RA-Account und Web-API-Key (API-Key niemals öffentlich teilen)

---

## `RA_config.json` (Beispiel)

Deine aktuelle Datei sollte so aussehen (Beispiel):

```json
{
    "GameID": 20774,
    "LeaderboardID": 85144
}
```

Ändere `LeaderboardID` oder `GameID` und speichere die Datei — das Poller-Script lädt die neue Konfiguration beim nächsten Poll automatisch.

---

## `write_ra_leaderboards.py` — Benutzung

1. Öffne die Datei und trage ganz oben deinen `USER` und `API_KEY` ein (beide Variablen sind aktuell leer):

```py
USER = "deinUser"
API_KEY = "DEIN_API_KEY"
```

2. Optional: Passe `OUTPUT_FILE`, `MY_FIRSTS_FILE`, `INTERVAL_SECONDS` oder `COUNT_FIRSTS_INTERVAL` an.

3. Starte das Script:

```bash
python write_ra_leaderboards.py
```

### Was das Script macht
- Lädt `RA_config.json` (hot-reload, prüft mtime).  
- Fragt das konfigurierte `LeaderboardID` ab und schreibt eine formatierte Datei `leaderboard_display.txt` (Standard: `C:\temp\leaderboard_display.txt`). Diese Datei ist für OBS-Textquellen geeignet.  
- Alle `COUNT_FIRSTS_INTERVAL` Sekunden (Standard: 30 s) wird `API_GetUserGameLeaderboards` abgefragt und die Datei `my_firsts.txt` geschrieben mit dem Format:

```
Top-Records on RA: 12 / 36 · ( 33.3%)
```

- Fehler (Network/HTTP/JSON) werden in die entsprechende Ausgabedatei geschrieben und auf der Konsole geloggt.

---

## `export_leaderboard_titles.py` — Benutzung

Dieses Script erzeugt eine Liste aller Leaderboards eines Spiels (ID + Title). Beispiel:

```bash
python export_leaderboard_titles.py
```

Standard-Output-Datei: `C:\temp\game_leaderboard_titles.txt` (jede Zeile: `ID\t: Title`).

**Beispielzeilen**:
```
85143	: Kanda Bridge(Kanjyo Inner) Class B
85144	: Kanda Bridge(Kanjyo Inner) Class C
```

Verwende diese IDs dann in `RA_config.json` als `LeaderboardID`.

---

## OBS-Integration

- Erstelle in OBS eine Textquelle, die aus Datei liest und auf die jeweiligen Ausgabedateien zeigt (z. B. `C:\temp\leaderboard_display.txt`).
- Für bestmögliche Spaltenausrichtung verwende eine **Monospace-Schrift** (Consolas, Courier New). Emojis funktionieren besser mit `Segoe UI Emoji`, sind aber proportional — das kann zu optischen Verschiebungen führen.

---

## Troubleshooting

- **401 Unauthorized**: API-Key oder Username falsch. Prüfe `USER` und `API_KEY`.
- **404 Not Found**: Falsche `LeaderboardID` oder falscher Endpoint. Prüfe die ID (mit `export_leaderboard_titles.py`) und die API-URLs.
- **JSON_DECODE_ERROR**: API hat kein JSON geliefert oder `RA_config.json` ist beschädigt.
- **Config-Änderung wird nicht übernommen**: auf einigen Dateisystemen hat `mtime` nur 1-s Auflösung; speichere die Datei atomar (z. B. als `tmp` schreiben und `os.replace`) oder warte eine Sekunde.

---

## Sicherheit

- Teile `API_KEY` niemals öffentlich (GitHub, Screenshots, Stream-Chat).  
- Wenn du die Keys aus der `RA_config.json` herausziehen willst, kann man das Script leicht anpassen, damit User/API-Key aus `RA_config.json` geladen werden (empfohlen).

---

## Weiteres / Ideen

- Optional: speichere `User`/`API_KEY` in `RA_config.json` und lade sie dynamisch.
- Optional: Schreibe eine Funktion, die per CLI einen Leaderboard-Wechsel direkt in `RA_config.json` schreibt.
