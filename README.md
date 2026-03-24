# Wordle Engine - Progetto di Programmazione

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![PyQt6](https://img.shields.io/badge/Framework-PyQt6-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Tests](https://img.shields.io/badge/Tests-Pytest-yellow.svg)

## 📌 Obiettivo del Progetto

L'obiettivo del team è stato quello di ricreare l'esperienza del celebre puzzle linguistico **Wordle**, focalizzandoci sulla pulizia del codice, sull'efficienza algoritmica e sull'ottimizzazione dell'esperienza utente. Il progetto gestisce database lessicali, logiche di confronto avanzate e un design dell'interfaccia moderno e responsivo.

## 🚀 Funzionalità Principali

- **Logica di Gioco**: Sistema di feedback immediato basato su tre stati (Corretto, Presente ma in posizione errata, Assente).
- **Gestione del Dizionario**: Dataset di parole di 5 lettere filtrato per escludere termini arcaici o eccessivamente complessi, garantendo giocabilità.
- **Interfaccia Utente (UI)**: Design minimalista progettato in **PyQt6** per mantenere alta la concentrazione del giocatore.

## 🏗️ Architettura Tecnica

Il lavoro segue una suddivisione modulare:

1.  **Frontend (GUI)**: Gestione della griglia dinamica e delle animazioni dei tasselli.
2.  **Game Logic (Core)**: Algoritmo di validazione dei tentativi, gestione "Daily Challenge" e "Training".
3.  **Data Handling**: Persistenza dei dati e gestione classifiche tramite **SQLite**.

### 🧠 Sfide Tecniche Superate

- **Gestione delle lettere doppie**: Ottimizzazione dell'algoritmo per evitare falsi positivi quando una lettera compare più volte nel tentativo ma una sola volta nella parola segreta.
- **Integrità dei dati**: Implementazione di sistemi di _rollback_ nelle transazioni del database per prevenire corruzioni in caso di errori di runtime.

## 🧪 Testing & Quality Assurance

Il software include una suite di test completa per garantire la stabilità dell'applicazione:

- **Unit Testing**: Copertura totale della logica di business (`core`).
- **GUI Testing**: Utilizzo di `pytest-qt` per verificare il comportamento delle finestre e le transizioni UI.
- **GitHub Actions**: Pipeline di CI per il Linting (Pylint) e l'esecuzione automatizzata dei test.

### ⚠️ Nota sulla Coverage e Test Skipped (CI/CD)

Durante l'esecuzione sulla pipeline di GitHub Actions, i test relativi all'interfaccia grafica (GUI) vengono **automaticamente saltati (skipped)**.

**Motivazione:** Le librerie grafiche PyQt6 richiedono un server display (X11/Wayland) per inizializzare i widget. Poiché l'ambiente di GitHub Actions è _headless_ (privo di interfaccia video), l'inizializzazione dei componenti UI fallirebbe a prescindere dalla correttezza del codice.

Abbiamo quindi scelto di documentare lo stato "skipped" in ambiente remoto come limitazione infrastrutturale nota, garantendo comunque l'esecuzione dei test sulla logica core e mantenendo i test GUI pronti per l'uso in ambiente locale (dove la copertura supera il **90%**).

## 🛠️ Installazione e Avvio

1.  **Installazione dipendenze**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Inizializzazione Database (Obbligatorio al primo avvio)**:
    Prima di lanciare l'applicazione, è necessario creare e popolare il database locale con il dizionario delle parole:

    ```bash
    python -m src.database.seed_db
    ```

3.  **Avvio del Gioco**:

    ```bash
    python main.py
    ```

4.  **Esecuzione Test**:
    ```bash
    pytest --cov=src tests/
    ```

## 👥 Team di Sviluppo

- **Andrea Lizzio**
- **Angelo Midulla**
- **Lillian Ferla**

---

_Progetto realizzato per il corso di Programmazione - Anno Accademico 2025/2026_
