import json
from datetime import datetime
from functools import wraps
import getopt
from time import mktime
import sys

from bs4 import BeautifulSoup
from flask import Flask, request, abort, redirect, render_template
import requests
from sqlalchemy import schema, types, orm
from sqlalchemy.engine import create_engine
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)

# Database...
metadata = schema.MetaData()

url_table = schema.Table('shitbct_url', metadata,
    schema.Column('id',
        types.Integer,
        schema.Sequence('shitbct_url_seq_id', optional=True),
        primary_key=True),
    schema.Column('url', types.Unicode(2000)),
    schema.Column('url_title', types.Unicode(1024)),
    schema.Column('public', types.Boolean(), default=False),
    schema.Column('created_at', types.DateTime(), default=datetime.now)
)

config_table = schema.Table('shitbct_config', metadata,
    schema.Column('id',
        types.Integer,
        schema.Sequence('shitbct_config_seq_id', optional=True),
        primary_key=True),
    schema.Column('key', types.String),
    schema.Column('value', types.String)
)


class ShitBucketUrl(object):
    pass


class ShitBucketConfig(object):
    pass

orm.mapper(ShitBucketUrl, url_table)
orm.mapper(ShitBucketConfig, config_table)


def make_db_session(app):
    db_engine = create_engine(app.config['DB_URI'], echo=True)
    metadata.bind = db_engine
    metadata.create_all(checkfirst=True)

    session = orm.scoped_session(orm.sessionmaker(bind=db_engine,
                                                  autoflush=True,
                                                  autocommit=False,
                                                  expire_on_commit=True))
    return session


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


@app.route('/')
@auth(abort=False)
def index(authenticated=True):
    urls = app.db_session.query(ShitBucketUrl).all()
    return render_template('index.html', urls=urls)


@app.route('/submit', methods=['POST'])
@auth
def submit():
    url = request.form['url']
    result = add_url(url)
    if result:
        return redirect('/')
    abort(409)


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    return 'Not fucking configured'


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
