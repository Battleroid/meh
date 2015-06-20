from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Board, Thread, FTSThread
from celery.result import AsyncResult
from func import update_threads
from flask_peewee.utils import object_list, PaginatedQuery

app = Flask(__name__)
app.config.from_object('config')

from func import celery
celery.init_app(app)

@app.route('/', methods=['GET'])
def home():
    recent_threads = Thread.select().limit(10).order_by(Thread.add_date.desc())
    total_threads = "{:,d}".format(Thread.select().count())
    return render_template('home.html', threads=recent_threads, total=total_threads)

@app.route('/browse/<int:page>')
@app.route('/browse')
def browse(page=1):
    threads = Thread.select().order_by(Thread.add_date.desc())
    pages = (threads.count() / 20) + 1
    return render_template('browse.html', threads=threads.paginate(page), page=page, pages=pages, total=threads.count())

@app.route('/search/')
def search():
    if request.args.get('q', None):
        q = request.args.get('q')
        query = (FTSThread
                .select(Thread, FTSThread)
                .join(Thread)
                .where(FTSThread.match(q)))
        return object_list('search.html', query, 'threads', q=q, total=query.count())
    else:
        return render_template('search.html')

@app.route('/refresh', methods=['GET'])
def refresh():
    recent_threads = Thread.select().limit(10).order_by(Thread.add_date.desc())
    return render_template('threads.html', threads=recent_threads)

@app.route('/update', methods=['POST'])
def update():
    task = update_threads.apply_async()
    return jsonify({}), 202, {'Location': url_for('status', task_id=task.id)}

@app.route('/stats')
def stats():
    total_threads = Thread.select().count()
    total_boards = Board.select().count()
    last_update = Thread.select(Thread.add_date).limit(1).order_by(Thread.add_date.desc()).get().add_date
    return jsonify(dict(
        total_threads=total_threads,
        total_boards=total_boards,
        last_update=last_update.strftime('%Y-%m-%d %H:%M:%S')))

@app.route('/status/<task_id>')
def status(task_id):
    task = update_threads.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = dict(
                state=task.state,
                current=0,
                total=150,
                status='Pending'
        )
    elif task.state != 'FAILURE':
        if not task.info:
            current = 1
            total = 1
            status = 'Done'
        else:
            current = task.info.get('current', 0)
            total = task.info.get('total', 150)
            status = task.info.get('status', 'grabbing')
        response = dict(
                state=task.state,
                current=current,
                total=total,
                status=status
        )
    else:
        # uh oh
        response = dict(
                state=task.state,
                current=1,
                total=1,
                status=str(task.info)
        )
    return jsonify(response)
        
