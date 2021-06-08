import os
import hashlib
import redis
from rq import Queue
from flask import Flask, jsonify, request, redirect, url_for, render_template, flash, Markup
from werkzeug.utils import secure_filename
from subprocess import check_call
import secrets

from model import predict

app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret
r = redis.Redis()
q = Queue(connection=r)

# Limit File size to 2GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 2 * 10**3

# Registered Services:
known_services = ["CATMAID", "NEUPRINT", "FLYWIRE", "FAFB", "HEMI"]
known_predict_types = ["POSITION", "NEURON"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')

@app.route('/', methods=['POST'])
def parse_form():
    uploaded_file = request.files['file']
    mail = request.form.get("email")
    service = request.form.get("service")
    predict_from = request.form.get("type")
    
    if not has_access(mail):
        flash(Markup(render_template("redirect_access.html")), category="error")
        return redirect(url_for('index'))
    elif not is_valid_option(service, predict_from):
        flash(Markup(render_template("redirect_options.html")), category="error")
        return redirect(url_for('index'))
    elif uploaded_file.filename == "":
        flash(Markup(render_template("redirect_nofile.html")), category="error")
        return redirect(url_for('index'))
    else:
        flash(Markup(render_template("redirect_uploading.html")), category="info")
        job = gen_job(mail, uploaded_file, service, predict_from)
        queue_job(job)
        flash(Markup(render_template("redirect_queued.html")), category="success")
        return redirect(url_for('index'))

def queue_job(job):
    task = q.enqueue(predict, job)
    print(f"Queued job {task.id} to {task.enqueued_at}")

def get_requests():
    rdir = "requests"
    requests = [os.path.join(rdir, f) for f in os.listdir(rdir) if f.endswith(".csv")]
    return requests

def gen_job(mail, uploaded_file, service, predict_from):
    requests = get_requests()
    request_id = len(requests)
    uid = get_user_id(mail)
    uploaded_file.save(os.path.join("requests", f"r_{uid}_{request_id}.csv"))
    request = {"uid": uid, "request_id": request_id, 
               "mail": mail, "service": service,
               "predict_from": predict_from}
    return request

def has_access(user):
    registered_users = [l.strip() for l in open('users.txt', 'r').readlines()]
    user_hash = hashlib.sha512(str.encode(user)).hexdigest()
    if user_hash in registered_users:
        return True
    return False

def get_user_id(user):
    registered_users = [l.strip() for l in open('users.txt', 'r').readlines()]
    user_hash = hashlib.sha512(str.encode(user)).hexdigest()
    uid = registered_users.index(user_hash)
    return uid

def is_valid_option(service, predict_from):
    if not service in known_services:
        return False
    if not predict_from in known_predict_types:
        return False
    if service != "CATMAID":
        return predict_from == "POSITION"
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
