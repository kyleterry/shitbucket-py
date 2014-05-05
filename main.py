import json
import getopt
import sys

from flask import Flask, request, abort, redirect, render_template
from werkzeug.contrib.fixers import ProxyFix

from shitbucket.routes import app as routes
from shitbucket.models import make_db_session, ShitBucketUrl, ShitBucketConfig


app = Flask(__name__, static_folder='shitbucket/static')
app.register_blueprint(routes)


def make_app(args):
    try:
        opts, args = getopt.getopt(args, ':d', ['db=',])
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
    app = make_app(sys.argv[1:])
    app.debug = True
    app.run()
