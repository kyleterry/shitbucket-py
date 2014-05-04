from functools import wraps

from bs4 import BeautifulSoup
from flask import (current_app, Blueprint, abort, request, redirect,
                   render_template)
import requests

from shitbucket.models import ShitBucketConfig, ShitBucketUrl

app = Blueprint('shitbucket', __name__, template_folder='templates')


def auth(*a, **k):
    def _auth(f):
        @wraps(f)
        def func(*args, **kwargs):
            # TODO: is the application even configured?

            if not hasattr(k, 'abort'):
                do_abort = True
            else:
                do_abort = k['abort']

            key = request.args.get('auth_key')
            q = current_app.db_session.query(ShitBucketConfig).filter(
                ShitBucketConfig.key == 'auth_key',
                ShitBucketConfig.value == key
            )
            if q.count() == 0:
                q = current_app.db_session.query(ShitBucketConfig).filter(
                    ShitBucketConfig.key == 'auth_key'
                )
                if do_abort:
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
    q = current_app.db_session.query(ShitBucketUrl).filter(
        ShitBucketUrl.url == url
    )
    if q.count() > 0:
        return False

    current_app.db_session.add(item)
    current_app.db_session.flush()
    current_app.db_session.commit()

    return True


@app.route('/')
@auth(abort=False)
def index(authenticated=True):
    urls = current_app.db_session.query(ShitBucketUrl).all()
    return render_template('index.html', urls=urls)


@app.route('/url/submit', methods=['POST'])
@auth
def url_submit():
    url = request.form['url']
    result = add_url(url)
    if result:
        return redirect('/')
    abort(409)


@app.route('/bash-history/submit', methods=['POST'])
@auth
def bash_history_submit():
    pass


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    return 'Not fucking configured'
