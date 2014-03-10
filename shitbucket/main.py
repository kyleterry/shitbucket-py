import json
from datetime import datetime
from functools import wraps
from time import mktime

from bs4 import BeautifulSoup
from flask import Flask, request, abort, redirect
import requests
from sqlalchemy import schema, types, orm
from sqlalchemy.engine import create_engine


app = Flask('shitbucket')

# Database...
metadata = schema.MetaData()
db_engine = create_engine('sqlite:////tmp/test.db', echo=True)

metadata.bind = db_engine
url_table = schema.Table('shitbct_url', metadata,
    schema.Column('id',
        types.Integer,
        schema.Sequence('shitbct_url_seq_id', optional=True),
        primary_key=True),
    schema.Column('url', types.Unicode(2000)),
    schema.Column('url_title', types.Unicode(1024)),
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

metadata.create_all(checkfirst=True)


class ShitBucketUrl(object):
    pass


class ShitBucketConfig(object):
    pass

orm.mapper(ShitBucketUrl, url_table)
orm.mapper(ShitBucketConfig, config_table)

session = orm.scoped_session(orm.sessionmaker(bind=db_engine, autoflush=True,
                             autocommit=False, expire_on_commit=True))


def add_url(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    url_title = soup.title.string

    item = ShitBucketUrl()
    item.url = url
    item.url_title = url_title

    # Does the URL exist?
    q = session.query(ShitBucketUrl).filter(ShitBucketUrl.url == url)
    if q.count() > 0:
        return False

    session.add(item)
    session.flush()
    session.commit()

    return True


def auth(f):
    @wraps(f)
    def func(*args, **kwargs):
        # TODO: is the application even configured?

        key = request.args.get('auth_key')
        q = session.query(ShitBucketConfig).filter(ShitBucketConfig.key=='auth_key',
                                                   ShitBucketConfig.value==key)
        if q.count() == 0:
            abort(401)
        return f(*args, **kwargs)
    return func


@app.route('/')
@auth
def index():
    return 'Nothing to see here. Yet.'


@app.route('/submit', methods=['POST'])
@auth
def submit():
    url = request.form['url']
    result = add_url(url)
    if result:
        return redirect('/')
    abort(409)


def get_app():
    return app


if __name__ == '__main__':
    app.debug = True
    app.run()