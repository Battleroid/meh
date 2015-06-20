from flask_celery import Celery
from celery import current_task
from models import Board, Thread, FTSThread
import json
import urllib2
from datetime import datetime

celery = Celery()

@celery.task(bind=True)
def update_threads(self):
    def get_json(board, pages=range(1, 11)):
        for page in pages:
            yield json.load(urllib2.urlopen('http://api.4chan.org/{board}/{page}.json'.format(board=board, page=page)))

    def check_threads(board):
        total_threads = 150
        finished = 0
        for page in get_json(board.name):
            page = page['threads']
            threads = filter(lambda x: 'com' in x['posts'][0].keys(), page)
            threads = filter(lambda x: not Thread.select().where(Thread.no == x['posts'][0]['no']).exists(), threads)
            for thread in threads:
                op = thread['posts'][0]
                no = op['no']
                post = op['com']
                time = datetime.fromtimestamp(op['time'])
                entry = Thread.create(board=board, no=no, post=post, add_date=time)
                FTSThread.create(thread=entry, post=post)
                finished += 1
                self.update_state(
                        state='PROGRESS',
                        meta={'current': finished, 'total': total_threads})
                print '{} added'.format(str(no))

    for board in Board.select():
        check_threads(board)

if __name__ == '__main__':
    update_threads()
