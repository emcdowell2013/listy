from flask import render_template, url_for, redirect, g, abort
from app import app
from .forms import TaskForm

@app.route("/", methods = ['GET', 'POST'])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        r.table('todos').insert({'name':form.label.data}).run(g.rdb_conn)
        return redirect(url_for('index'))
    selection = list(r.table('todos').run(g.rdb_conn))
    return render_template('index.html', form=form, tasks=selection)

@app.route("/delete/<string:task_id>")
def delete_task(task_id):
    #form = TaskForm()
    r.table('todos').filter({"id": task_id}).delete().run(g.rdb_conn)
    return redirect(url_for('index'))
    #selection = list(r.table('todos').run(g.rdb_conn))
    #return render_template('index.html', form=form, tasks=selection)


# rethink imports
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError

# rethink config
r = rdb.RethinkDB()
RDB_HOST = 'localhost'
RDB_PORT = 28015
LISTY_DB = 'listy'

# db setup; only run once
def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(LISTY_DB).run(connection)
        r.db(LISTY_DB).table_create('todos').run(connection)
        print('Database setup completed.')
    except RqlRuntimeError:
        print('Database already exists.')
    finally:
        connection.close()
dbSetup()

# open connection befor each request
@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=LISTY_DB)
    except RqlRuntimeError:
        abort(503, 'Database connection could not be established.')

# close the connection after each request
@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass
