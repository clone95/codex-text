from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

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
                    description TEXT
                )''')
    # Check if table is empty
    c.execute('SELECT COUNT(*) FROM items')
    count = c.fetchone()[0]
    if count == 0:
        sample_items = [
            ('Pen', 50, 'Blue ink pen'),
            ('Notebook', 20, '200 pages notebook'),
            ('Stapler', 5, 'Standard stapler'),
            ('Paper Clips', 100, 'Box of paper clips'),
            ('Highlighter', 30, 'Yellow highlighter'),
            ('Folder', 15, 'A4 folder'),
            ('Sticky Notes', 25, 'Pack of sticky notes'),
            ('Marker', 10, 'Permanent marker'),
            ('Scissors', 8, 'Office scissors'),
            ('Tape', 12, 'Adhesive tape roll')
        ]
        c.executemany('INSERT INTO items (name, quantity, description) VALUES (?, ?, ?)', sample_items)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name, quantity, description FROM items')
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    description = request.form.get('description', '')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO items (name, quantity, description) VALUES (?, ?, ?)',
              (name, quantity, description))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE items SET quantity = ? WHERE id = ?', (quantity, item_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
