# 🏃 Laufgruppe Dashboard

Dieses Tool besteht aus zwei Dateien:
- `laufgruppe.xlsx` – Excel-Datei zum Verwalten der Kinder und Zeiten
- `dashboard.py` – Streamlit-App für die visuelle Auswertung

---

## ⚙️ Installation (einmalig)

```bash
pip install streamlit pandas openpyxl plotly
```

---

## 🚀 Starten

1. Beide Dateien im gleichen Ordner speichern
2. Terminal öffnen, in den Ordner wechseln
3. Starten mit:

```bash
streamlit run dashboard.py
```

Der Browser öffnet sich automatisch unter http://localhost:8501

---

## 📝 Daten eintragen

### Neue Kinder → Sheet „Läufer"
Trage Name, Jahrgang und Gruppe ein.

### Wöchentliche Zeiten → Sheet „Zeiten"
| Datum | Name | Zeit (mm:ss) | Anmerkung |
|-------|------|-------------|-----------|
| 06.01.2025 | Anna Müller | 25:34 | |

> **Wichtig:** Name genau wie im Läufer-Sheet schreiben!  
> Zeit im Format `MM:SS` (z.B. `25:34`)

---

## 📊 Dashboard-Funktionen

| Seite | Inhalt |
|-------|--------|
| 🏆 Podium & Übersicht | Teilnahme-Podium, Bestzeiten, Verlauf aller Kinder |
| 👤 Einzelne Läufer | Persönliche Statistiken, Zeitverlauf, Verbesserung |
