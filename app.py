from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
from datetime import datetime
import csv
import io

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'inventory.db')

# Initialize database with 10 items if it doesn't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    description TEXT,
                    last_updated TEXT
                )''')
    # Ensure last_updated column exists
    c.execute("PRAGMA table_info(items)")
    cols = [r[1] for r in c.fetchall()]
    if 'last_updated' not in cols:
        c.execute('ALTER TABLE items ADD COLUMN last_updated TEXT')
    # Check if table is empty
    c.execute('SELECT COUNT(*) FROM items')
    count = c.fetchone()[0]
    if count == 0:
        now = datetime.utcnow().isoformat()
        sample_items = [
            ('Pen', 50, 'Blue ink pen', now),
            ('Notebook', 20, '200 pages notebook', now),
            ('Stapler', 5, 'Standard stapler', now),
            ('Paper Clips', 100, 'Box of paper clips', now),
            ('Highlighter', 30, 'Yellow highlighter', now),
            ('Folder', 15, 'A4 folder', now),
            ('Sticky Notes', 25, 'Pack of sticky notes', now),
            ('Marker', 10, 'Permanent marker', now),
            ('Scissors', 8, 'Office scissors', now),
            ('Tape', 12, 'Adhesive tape roll', now)
        ]
        c.executemany('INSERT INTO items (name, quantity, description, last_updated) VALUES (?, ?, ?, ?)', sample_items)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'name')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT id, name, quantity, description, last_updated FROM items'
    params = []
    if search:
        query += ' WHERE name LIKE ?'
        params.append(f'%{search}%')
    if sort == 'quantity':
        query += ' ORDER BY quantity ASC'
    else:
        query += ' ORDER BY name ASC'
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items, search=search, sort=sort)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    description = request.form.get('description', '')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO items (name, quantity, description, last_updated) VALUES (?, ?, ?, ?)',
              (name, quantity, description, now))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('UPDATE items SET quantity = ?, last_updated = ? WHERE id = ?',
              (quantity, now, item_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        description = request.form.get('description', '')
        now = datetime.utcnow().isoformat()
        c.execute('UPDATE items SET name=?, quantity=?, description=?, last_updated=? WHERE id=?',
                  (name, quantity, description, now, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        c.execute('SELECT id, name, quantity, description FROM items WHERE id=?', (item_id,))
        item = c.fetchone()
        conn.close()
        return render_template('edit.html', item=item)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT name, quantity, description, last_updated FROM items ORDER BY name ASC')
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'quantity', 'description', 'last_updated'])
    writer.writerows(rows)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='inventory.csv')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
