# GitHub Copilot Instructions

## Projekt
Digital Twin Projekt für Glukose- und Insulinmodellierung.

## Technologie-Stack
- Sprache: Python 3.13
- Framework: Kein Framework (aktuell)
- Wichtige Libraries: Werden bei Bedarf ergänzt

## Code-Konventionen
- Style Guide: Google Python Style Guide
- Zeilenlänge: 79 Zeichen
- Naming: snake_case (Variablen/Funktionen), PascalCase (Klassen)

## Pflicht bei jeder Funktion
- Type Hints (Python: PEP 484)
- Docstring im Google-Format
- Fehlerbehandlung mit spezifischen Exceptions

## Verboten
- Bare `except:` ohne Typ
- Globale mutable Variablen
- Hardcodierte Werte (stattdessen Konstanten)

## Prompt-Vorlage für Copilot-Anfragen
Wenn du Code anforderst, nutze diese Vorlage:
"Erstelle eine Funktion die [BESCHREIBUNG].
Anforderungen: Type Hints, Google Docstring, snake_case, max 79 Zeichen."
