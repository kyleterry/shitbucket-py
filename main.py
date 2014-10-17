from datetime import datetime
import os
import hashlib
import getopt
import sys

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from shitbucket.routes import app as routes
from shitbucket.models import make_db_session, ShitBucketConfig
from shitbucket.config import get_settings


app = Flask(__name__, static_folder='shitbucket/static')
app.register_blueprint(routes)

# Sometimes I sit alone in my room and cry

def bootstrap(app):
    q = app.db_session.query(ShitBucketConfig).filter(
        ShitBucketConfig.key == 'bootstrapped'
    )
    if q.count() > 0:
        print("Already boostrapped!")
        sys.exit(1)

    key = hashlib.sha256(os.urandom(16)).hexdigest()

    configkey = ShitBucketConfig()
    configkey.key = 'auth_key'
    configkey.value = key

    configbootstrapped = ShitBucketConfig()
    configbootstrapped.key = 'bootstrapped'
    configbootstrapped.Value = datetime.now()

    app.db_session.add(configkey)
    app.db_session.add(configbootstrapped)
    app.db_session.flush()
    app.db_session.commit()

    print("Your authorization key is ", key)

def make_app(db, config_file):
    # handle settings
    app.config['DB_URI'] = db
    app.config['settings'] = get_settings(config_file)

    session = make_db_session(app)
    app.db_session = session
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], ':d:cb', ['db=', 'config='])
    except getopt.GetoptError:
        print("Usage?")
        sys.exit(1)
    config_file = None
    do_bootstrap = False
    for opt, arg in opts:
        if opt == '-h':
            print("Usage?")
            sys.exit()
        elif opt == '-b':
            do_bootstrap = True
        elif opt in ('--db', '-d'):
            db = arg
        elif opt in ('--config', '-c'):
            config_file = arg
    app = make_app(db, config_file)
    app.debug = True
    if do_bootstrap:
        bootstrap(app)
        sys.exit(0)
    else:
        app.run()  # run where? I'm out of places to run.
