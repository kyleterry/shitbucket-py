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

            if 'abort' not in k:
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
                        return redirect('/configure')
                    else:
                        return abort(401)
                else:
                    kwargs['authenticated'] = False
            kwargs['auth_key'] = key
            return f(*args, **kwargs)
        return func
    if len(a) == 1 and callable(a[0]):
        return _auth(a[0])
    else:
        return _auth


def add_url(url, source='api'):
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text)
    url_title = None
    if soup.title:
        url_title = soup.title.string

    item = ShitBucketUrl()
    item.url = url
    item.url_title = url_title
    item.source = source

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


@app.errorhandler(409)
def conflict(e):
    return 'Conflicting with my other personality. I\'ve gone mental.'


@app.route('/')
@auth(abort=False)
def index(authenticated=True, auth_key=None):
    if authenticated:
        urls = current_app.db_session.query(ShitBucketUrl).all()
    else:
        urls = current_app.db_session.query(ShitBucketUrl).filter(
            ShitBucketUrl.public == True
        )
    return render_template('index.html', urls=urls, auth_key=auth_key)


@app.route('/url/submit', methods=['GET','POST'])
@auth
def url_submit(auth_key=None):
    if request.method == 'POST':
        source = request.form['source'] if 'source' in request.form else 'api'
        url = request.form['url']
        result = add_url(url, source)
        if result:
            if source == 'web':
                return redirect('/?auth_key={}'.format(auth_key), code=302)
            return 'I heard the bell ring, so I ran to class.'
        abort(409)
    return render_template('add.html', auth_key=auth_key)


@app.route('/bash-history/submit', methods=['POST'])
@auth
def bash_history_submit():
    pass


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    return 'Not fucking configured'
