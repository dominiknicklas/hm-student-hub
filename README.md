# 🎓 Student Hub FK07

## 🔍 Ziel der Anwendung

**Student Hub FK07** ist ein webbasiertes Informationssystem für Studierende der Fakultät für Informatik und Mathematik (FK07) an der Hochschule München.  
Ziel ist es, alle studienrelevanten Informationen zentral und übersichtlich bereitzustellen sowie den Studierenden die Möglichkeit zu bieten, eigene Erfahrungen mit Professor:innen öffentlich zu teilen.
Im Gegensatz zur derzeit ausschließlich intern zugänglichen Evaluation sind diese Bewertungen für alle Studierenden einsehbar.


## ✨ Hauptfunktionen

Die Anwendung basiert auf einem **React + TypeScript Frontend** und einem **FastAPI + SQLite Backend**. Sie unterstützt die digitale Studienorganisation durch folgende Funktionen:

- 🧑‍🎓 Anlegen eines **persönlichen Profils**
- 📄 **PDF-Notenblatt hochladen** und automatisch analysieren (Noten, ECTS, Durchschnittsnote)
- 📅 **Stundenpläne und Prüfungstermine** abrufen – je nach gewählter Studiengruppe
- 📧 **E-Mail-Benachrichtigung** über bevorstehende Prüfungen (7 Tage im Voraus)
- 📊 Visualisierung des **Studienfortschritts**
- ⭐ **Professoren bewerten** – ein selbst trainiertes **Machine-Learning-Modell** erkennt toxische Sprache und filtert unpassende Bewertungen
- 🔍 **Scraping aktueller Daten** von:
  - der [ZPA-Seite](https://zpa.cs.hm.edu/public/) (Studiengruppen, Vorlesungen, Prüfungen)
  - der [FK07-Professurenseite](https://cs.hm.edu/fakultaet/personen/professuren.de.html) (Professorendetails)


## 🚀 Starten der Anwendung

### ⚙️ Voraussetzungen

- `npm` und `Python` müssen auf dem System installiert sein  
  - Empfohlen wird **Python 3.12**, da neuere Versionen unter Umständen nicht mit TensorFlow kompatibel sind.

- Das **ML-Modell für die Bewertungstexte** wird **nicht mitgeliefert**, da es zu groß ist.  
  → Vor dem Start der Anwendung muss das Modell eigenständig trainiert und gespeichert werden.  
  Dafür ist das **Jupyter-Notebook** unter `/student_hub/model_training` von oben bis unten einmal vollständig auszuführen.

- *(Optional)*: Der **E-Mail-Versand** ist standardmäßig deaktiviert, um keine privaten Zugangsdaten in der Anwendung zu speichern.  
  Statt einer tatsächlichen E-Mail wird der Inhalt lediglich in der Konsole ausgegeben.  
  → Wer reale E-Mails versenden möchte, muss einen eigenen SMTP-Server bzw. Absender konfigurieren.  
  Die entsprechenden Einstellungen können in `/student_hub/mailing.py` innerhalb der Funktion `send_exam_reminder_email` an den gekennzeichneten Stellen vorgenommen werden.


### Startup

**Backend Setup:** Ein neues Terminal öffnen und in das Root Verzeichnis des Projekts wechseln (Projekt-Root: `/student_hub`)

```bash
pip3 install -r student_hub/requirements.txt
python3 -m student_hub.main
```


**Frontend Setup:** Ein neues Terminal öffnen und in das Root Verzeichnis des Projekts wechseln
```bash
cd student_hub_frontend
npm install
npm run dev
```

---

## 🖥️ Nutzung der Anwendung

### Zugriff auf die Anwendung

- Sobald die Anwendung läuft, öffne im Browser: [http://localhost:5173](http://localhost:5173)
- Du landest auf dem Startbildschirm, auf dem du dich registrieren oder einloggen kannst.

### Registrierung

1. Persönliche Daten eingeben  
2. Gültigen offiziellen Leistungsnachweis (PDF) hochladen  
3. Aktuelle Studiengruppe auswählen → basierend darauf werden automatisch die zugehörigen Kurse ermittelt

---

### Funktionen nach dem Login

- Übersicht über den Studienverlauf: Noten, Durchschnittsnote, gesamter ECTS-Stand
- Persönlichen Stundenplan anzeigen und als Kalenderdatei exportieren
- Leistungsnachweis und Studiengruppe jederzeit aktualisieren
- Professor:innen suchen und bewerten

---

### Bewertungssystem für Professor:innen

- Über die Suchfunktion kann jede:r Professor:in der FK07 aufgerufen werden (inkl. „Max Mustermann“ als Testprofil)
- Auf dem Profil sind bestehende Bewertungen anderer Studierender sichtbar
- Eigene Bewertungen können abgegeben werden
  - Ein selbst trainiertes **Machine Learning Modell** prüft die Texteingabe auf toxische Sprache
  - Respektlose oder beleidigende Kommentare werden automatisch abgelehnt und nicht veröffentlicht

---

### Automatischer E-Mail-Versand von Prüfungserinnerungen

Beim Start der Anwendung sowie **täglich um 9 Uhr** prüft ein integrierter Scheduler automatisch, ob für einzelne Nutzer:innen eine Prüfung in genau 7 Tagen ansteht.

- Wird eine solche Prüfung gefunden, erhalten die betroffenen Studierenden eine **automatische Erinnerungs-E-Mail** mit allen relevanten Informationen.
- Diese Funktion erfordert keine manuelle Interaktion – sie läuft vollständig im Hintergrund.

