# mah_ki_demo

## Inhaltsverzeichnis

- [Einführung](#einführung)
- [Installation](#installation)
- [Benutzung](#benutzung)
- [Abhängigkeiten](#abhängigkeiten)
- [Beitragen](#beitragen)
- [Lizenz](#lizenz)

## Einführung

`mah_ki_demo`  **Bitte beachten Sie, dass es sich um einen simplen Prototyp für einen Vortag handelt und dieser lediglich zu Lernzwecken dient. Eine Verwendung in Produktivumgebungen wird nicht empfohlen.**

Um den vollen Funktionsumfang zu gewährleisten, muss zusätzlich ein lokales Language Model (LLM) laufen, beispielsweise mittels [LM Studio](https://lmstudio.ai/). Dies ermöglicht eine weitergehende Verarbeitung und Analyse der transkribierten Texte.

## Installation

Um `mah_ki_demo` auf Ihrem Rechner zu installieren und einzurichten, folgen Sie diesen Schritten:

1. Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist.
2. Clonen Sie dieses Repository auf Ihren lokalen Rechner.
3. Navigieren Sie zum Projektverzeichnis und erstellen Sie eine virtuelle Umgebung:

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
    OPENAI_API_KEY="Ihr_OpenAI_API_Schlüssel"
    ```


## Benutzung

Nach der Installation des Projekts und des Whisper-Modells, verschieben Sie das heruntergeladene Modell nach `/mah_ki_demo/models`. Um das kompilierte Modell zu verwenden, führen Sie den folgenden Befehl in Ihrem Terminal aus:

## Abhängigkeiten

`mah_ki_demo` benötigt folgende Abhängigkeiten:

- **Python 3**: [Installationsanleitung](https://www.python.org/downloads/)
- **Virtuelle Umgebung**: In Python 3 enthalten
- **Erforderliche Python-Pakete**: In `requirements.txt` aufgelistet
- **`mah_ki_demo` für die Kompilierung des Whisper-Modells**: [GitHub-Repository](https://github.com/Freakrider/mah_ki_demo)

## Beitragen

Wir begrüßen Beiträge zum Projekt `mah_ki_demo`! Um beizutragen:

1. Forke das Repository.
2. Erstelle einen neuen Branch für dein Feature oder deinen Fix.
3. Committe deine Änderungen und pushe sie zu deinem Fork.
4. Reiche einen Pull Request mit einer klaren Beschreibung deiner Änderungen ein.
