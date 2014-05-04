from functools import wraps

from bs4 import BeautifulSoup
from flask import Blueprint, abort, request, redirect, render_template
import requests

from shitbucket.models import ShitBucketConfig, ShitBucketUrl, make_db_session

app = Blueprint('shitbucket', __name__, template_folder='templates')
app = make_db_session(app)


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
