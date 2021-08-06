from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
Bootstrap(app)
db_name = '../door.db'

#routes
@app.route('/')
def index():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        door_logs = cur.execute("SELECT * FROM door_logs").fetchall()
        print(door_logs)
        return render_template('list.html', door_logs=door_logs)
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


if __name__ == '__main__':
    app.run(debug=True, port=80)