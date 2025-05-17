from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os
from datetime import datetime
import csv

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'inventory.db')


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS items (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               quantity INTEGER NOT NULL DEFAULT 0,
               description TEXT,
               last_updated TEXT NOT NULL
           )'''
    )
    c.execute('SELECT COUNT(*) FROM items')
    if c.fetchone()[0] == 0:
        now = datetime.now().isoformat(timespec="seconds")
        sample_items = [
            ("Pen", 50, "Blue ink pen", now),
            ("Notebook", 20, "200 pages notebook", now),
            ("Stapler", 5, "Standard stapler", now),
            ("Paper Clips", 100, "Box of paper clips", now),
            ("Highlighter", 30, "Yellow highlighter", now),
            ("Folder", 15, "A4 folder", now),
            ("Sticky Notes", 25, "Pack of sticky notes", now),
            ("Marker", 10, "Permanent marker", now),
            ("Scissors", 8, "Office scissors", now),
            ("Tape", 12, "Adhesive tape roll", now)
        ]
        c.executemany(
            'INSERT INTO items (name, quantity, description, last_updated) VALUES (?, ?, ?, ?)',
            sample_items
        )
    conn.commit()
    conn.close()


@app.route('/')
def index():
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'name')
    query = 'SELECT * FROM items'
    params = []
    if search:
        query += ' WHERE name LIKE ?'
        params.append(f'%{search}%')
    if sort not in {'name', 'quantity', 'last_updated'}:
        sort = 'name'
    query += f' ORDER BY {sort}'

    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)


@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    description = request.form.get('description', '')
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO items (name, quantity, description, last_updated) VALUES (?, ?, ?, ?)',
        (name, quantity, description, now)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = get_connection()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        description = request.form.get('description', '')
        now = datetime.now().isoformat(timespec="seconds")
        c.execute(
            'UPDATE items SET name = ?, quantity = ?, description = ?, last_updated = ? WHERE id = ?',
            (name, quantity, description, now, item_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = c.fetchone()
        conn.close()
        if not item:
            return redirect(url_for('index'))
        return render_template('edit.html', item=item)


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/export')
def export_csv():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT name, quantity, description, last_updated FROM items ORDER BY name')
    rows = c.fetchall()
    conn.close()
    def generate():
        yield 'name,quantity,description,last_updated\n'
        for row in rows:
            yield f"{row['name']},{row['quantity']},{row['description']},{row['last_updated']}\n"

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=inventory.csv'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
