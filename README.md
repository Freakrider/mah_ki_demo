# mah_ki_demo

## Inhaltsverzeichnis

- [Einführung](#einführung)
- [Installation](#installation)
- [Benutzung](#benutzung)
- [Abhängigkeiten](#abhängigkeiten)
- [Beitragen](#beitragen)

## Einführung

`mah_ki_demo` **Bitte beachten Sie, dass es sich um einen simplen Prototyp für einen Vortrag handelt und dieser lediglich zu Lernzwecken dient. Eine Verwendung in Produktivumgebungen wird nicht empfohlen.**

Um den Funktionsumfang zu gewährleisten, muss zusätzlich ein locales LLM laufen, mittels [OLLAMA](https://ollama.com/). 

## Installation

Um `mah_ki_demo` auf Ihrem Rechner zu installieren und einzurichten, folgen Sie diesen Schritten:

1. Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist.
2. Klonen Sie dieses Repository auf Ihren lokalen Rechner:

    ```bash
    git clone https://github.com/Freakrider/mah_ki_demo.git
    cd mah_ki_demo
    ```

3. Erstellen Sie eine virtuelle Umgebung:

    ```bash
    python3 -m venv .venv
    ```

4. Aktivieren Sie die virtuelle Umgebung:

    ```bash
    source .venv/bin/activate
    ```

5. Installieren Sie die erforderlichen Pakete:

    ```bash
    pip install -U -r requirements.txt
    ```

6. Fügen Sie eine `.env`-Datei hinzu, um Ihren OpenAI-API-Schlüssel zu hinterlegen:

    ```env
    FLASK_DEBUG=true
    FLASK_APP=app
    ```

## Benutzung

Nach der Installation des Projekts können Sie den Flask-Server starten:

```bash
flask run
```

Stellen Sie sicher, dass das LLM / llama3 läuft, bevor Sie Anfragen an den Server stellen. Verwenden Sie [OLLAMA](https://ollama.com/).

## Abhängigkeiten

`mah_ki_demo` benötigt folgende Abhängigkeiten:

- **Python 3**: [Installationsanleitung](https://www.python.org/downloads/)
- **Virtuelle Umgebung**: In Python 3 enthalten
- **Erforderliche Python-Pakete**: In `requirements.txt` aufgelistet

## Beitragen

Wir begrüßen Beiträge zum Projekt `mah_ki_demo`! Um beizutragen:

1. Forke das Repository.
2. Erstelle einen neuen Branch für dein Feature oder deinen Fix.
3. Committe deine Änderungen und pushe sie zu deinem Fork.
4. Reiche einen Pull Request mit einer klaren Beschreibung deiner Änderungen ein.
