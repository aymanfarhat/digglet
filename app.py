import flask
from flask import render_template
from flask import Response
from redis import Redis
from rq import Queue
import gmail

app = flask.Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    if 'credentials' in flask.session:
        return flask.redirect(flask.url_for('dashboard'))

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = gmail.get_credentials(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))

    else:
        return render_template('dashboard.html')


@app.route('/oauth2callback')
def oauth2callback():
    flow = gmail.get_auth_flow(flask.url_for('oauth2callback', _external=True))

    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()

        return flask.redirect(auth_uri)

    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()

    return flask.redirect(flask.url_for('dashboard'))


@app.route('/fetchmails')
def fetchmails():
    q = Queue(connection=Redis())
    job = q.enqueue(gmail.process_user_messages_async, flask.session['credentials'])

    return flask.jsonify({'jobId': job.get_id()})


@app.route('/checkstatus/<job_id>')
def checkstatus(job_id):
    q = Queue(connection=Redis())

    job = q.fetch_job(job_id)

    return flask.jsonify({'result': job.return_value, 'status': job.get_status()})


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run(debug=True)
