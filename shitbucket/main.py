import json
from functools import wraps
import getopt
from time import mktime
import sys

from bs4 import BeautifulSoup
from flask import Flask, request, abort, redirect, render_template
import requests
from werkzeug.contrib.fixers import ProxyFix

from .routes import app as routes
from .models import make_db_session, ShitBucketUrl, ShitBucketConfig


app = Flask(__name__)
app.add_blueprint(routes)


def add_url(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    url_title = soup.title.string

    item = ShitBucketUrl()
    item.url = url
    item.url_title = url_title

    # Does the URL exist?
    q = app.db_session.query(ShitBucketUrl).filter(ShitBucketUrl.url == url)
    if q.count() > 0:
        return False

    app.db_session.add(item)
    app.db_session.flush()
    app.db_session.commit()

    return True


def auth(*a, **k):
    def _auth(f):
        @wraps(f)
        def func(*args, **kwargs):
            # TODO: is the application even configured?

            key = request.args.get('auth_key')
            q = app.db_session.query(ShitBucketConfig).filter(ShitBucketConfig.key=='auth_key',
                                                    ShitBucketConfig.value==key)
            if q.count() == 0:
                q = app.db_session.query(ShitBucketConfig).filter(ShitBucketConfig.key=='auth_key')
                if k['abort']:
                    if q.count() == 0:
                        redirect('/configure')
                    else:
                        abort(401)
                else:
                    kwargs['authenticated'] = False
            return f(*args, **kwargs)
        return func
    if len(a) == 1 and callable(a[0]):
        return _auth(a[0])
    else:
        return _auth



def main(argv):
    try:
        opts, args = getopt.getopt(argv, ':d', ['db=',])
    except getopt.GetoptError:
        print("Usage?")
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage?")
            sys.exit()
        elif opt in ('--db', '-d'):
            app.config['DB_URI'] = arg
    session = make_db_session(app)
    app.db_session = session
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


if __name__ == '__main__':
    app = main(sys.argv[1:])
    app.debug = True
    app.run()
