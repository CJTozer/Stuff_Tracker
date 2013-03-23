import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from Resource import Resource
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt               
from flask.helpers import send_file
import time, traceback, os
from datetime import datetime

# Configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'data', 'stuff_tracker.db')
IMG_BASE = os.path.join(os.path.dirname(__file__), 'img')
DEBUG = False 
SECRET_KEY = '1eV6BSdsNTVT'
USERNAME = 'chris'
PASSWORD = '!bootstrap'

# Application
app = Flask(__name__)
app.config.from_object(__name__)

# Database functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
@app.before_request
def before_request():
    g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_resources():         
    return render_template('resources.html', resources=get_all_resources())

@app.route('/add_resource', methods=['POST'])
def add_resource():
    if not session.get('logged_in'):
        abort(401)
    update_db('insert into resources (name) values (?)', (request.form['resource_name'],))
    flash('New resource was successfully added')
    return redirect(url_for('show_resources'))

@app.route('/add_component/<int:res_id>', methods=['POST'])
def add_component(res_id):
    if not session.get('logged_in'):
        abort(401)
    update_db('insert into components (res_id, name, time, complete) values (?, ?, ?, ?)',
              (res_id, request.form['component_name'], 0.0, False))
    flash('New component was successfully added')
    return redirect(url_for('show_resources'))

@app.route('/spend_time/<int:comp_id>/<int:time>', methods=['POST'])
def spend_time(comp_id, time):
    if not session.get('logged_in'):
        abort(401)
    update_times()
    update_db('update components set time=time+? where comp_id=?', (time, comp_id))
    update_times()    
    return redirect(url_for('show_resources'))

@app.route('/complete/<int:comp_id>', methods=['POST'])
def complete(comp_id):
    if not session.get('logged_in'):
        abort(401)
    update_db('update components set complete=? where comp_id=?', (True, comp_id))
    return redirect(url_for('show_resources'))

@app.route('/get_graph/<string:graph_type>')
def get_graph(graph_type):
    graph_name = 'graph_%s.png' % graph_type
    url = os.path.join(IMG_BASE, graph_name)
    return send_file(url, mimetype="image/png")

@app.route('/update_graph/<string:graph_type>')
def update_graph(graph_type):
    update_times()
    
    graph_name = 'graph_%s.png' % graph_type
    url = os.path.join(IMG_BASE, graph_name)
    resource_map = {res.res_id : res.name for res in get_all_resources()}
    plots = []
    plot_names = [] 
    
    series = {}
    db_data = query_db('select * from resource_time_tracking order by timestamp')
    for row in db_data:
        res_id = row['res_id']
        if not series.has_key(res_id):
            series[res_id] = {'x_vals':[], 'y_vals':[]}
        series[res_id]['x_vals'].append(datetime.fromtimestamp(row['timestamp']))
        series[res_id]['y_vals'].append(row['time_spent'] * 1.0 / 60.0  )
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for res_id in series.keys():
        plot_name = resource_map[res_id]
        new_plot, = ax.plot(series[res_id]['x_vals'], series[res_id]['y_vals'], label=plot_name)
        plots.append(new_plot)
        plot_names.append(plot_name)
    
    ax.legend(plots, plot_names, loc=2)
    fig.autofmt_xdate()
    fig.savefig(url)
    
    return send_file(url, mimetype="image/png")


# Utilities
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def update_db(update, args=()):
    g.db.execute(update, args)
    g.db.commit()

def get_all_resources():
    return [Resource(db_row,
                     query_db('select * from components where res_id = ? order by comp_id',
                              args=(db_row['res_id'],)))
            for db_row in query_db('select * from resources order by res_id')]

def update_times():
    for resource in get_all_resources():
        update_db('insert into resource_time_tracking (timestamp, res_id, time_spent) values (?, ?, ?)',
                  (time.time(), resource.res_id, resource.total_time()))
        
















# @@@ For reference...

@app.route('/update/<int:entry_id>/<string:text>', methods=['GET', 'POST'])
def update_entry(entry_id, text):
    g.db.execute('update entries set text=? where entry_id=?', (text, entry_id))
    g.db.commit()
    flash('Updated entry %d' % entry_id)
    return redirect(url_for('show_resources'))

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text, priority) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], request.form['priority']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_resources'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_resources'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_resources'))

# Utilities
@app.template_filter('get_class_for_entry')
def get_class_for_entry(entry):
    # FUTURE - if done => alert-success
    print entry
    classes = {
        0 : "alert-block",
        1 : "alert alert-info",
        2 : "alert",
        3 : "alert alert-error"}
    return classes[entry['priority'] or 0]

# Script entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0')
