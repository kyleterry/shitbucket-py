from flask import Flask, Blueprint

app = Blueprint('shitbucket')

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
