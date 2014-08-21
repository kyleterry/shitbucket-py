import json
import getopt
import sys

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from shitbucket.routes import app as routes
from shitbucket.models import make_db_session
from shitbucket.config import get_settings


app = Flask(__name__, static_folder='shitbucket/static')
app.register_blueprint(routes)

# Sometimes I sit alone in my room and cry

def make_app(args):
    try:
        opts, args = getopt.getopt(args, ':d:c', ['db=', 'config='])
    except getopt.GetoptError:
        print("Usage?")
        sys.exit(1)
    config_file = None
    for opt, arg in opts:
        if opt == '-h':
            print("Usage?")
            sys.exit()
        elif opt in ('--db', '-d'):
            app.config['DB_URI'] = arg
        elif opt in ('--config', '-c'):
            config_file = arg

    # handle settings
    app.config['settings'] = get_settings(config_file)

    session = make_db_session(app)
    app.db_session = session
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


if __name__ == '__main__':
    app = make_app(sys.argv[1:])
    app.debug = True
    app.run() # run where? I'm out of places to run.
