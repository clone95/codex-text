# codex-text

This repository contains a minimal inventory management application built with Flask and SQLite. It provides a simple web interface to view, search, sort, edit, export and delete items.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open your browser at `http://127.0.0.1:5000` to manage the inventory.

The database is stored locally in `inventory.db` and is automatically initialized with 10 sample items on first run.

## Features

- Search items by name and sort by name or quantity
- Track the last updated timestamp for each item
- Edit item details including name, quantity and description
- Export the inventory to a CSV file
