# codex-text

This repository contains a simple inventory management web application built with Flask and SQLite.
It starts with ten sample items and lets you search, sort, add, edit, delete, and export the inventory.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in your browser.

The database is stored locally in `inventory.db` and is automatically initialized
with sample data on first run.
