import os
import hashlib
from flask import Flask, jsonify, request, redirect, url_for, render_template, flash, Markup
from flask_restful import Api, Resource
from model import get_neurotransmitter_predictions
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
api = Api(app)
secret = secrets.token_urlsafe(32)
app.secret_key = secret

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
        uploaded_file.save(os.path.join("requests", secure_filename(f"{mail}.csv")))
        flash(Markup(render_template("redirect_queued.html")), category="success")
        return redirect(url_for('index'))

def has_access(user):
    registered_users = [l.strip() for l in open('users.txt', 'r').readlines()]
    user_hash = hashlib.sha512(str.encode(user)).hexdigest()
    if user_hash in registered_users:
        return True
    return False

def is_valid_option(service, predict_from):
    if not service in known_services:
        return False
    if not predict_from in known_predict_types:
        return False
    if service != "CATMAID":
        return predict_from == "POSITION"
    return True

def read_skids_csv(csv_path):
    """
    The csv needs to have one column called 'skid'
    """
    data = pandas.read_csv(csv_path)
    skids = data["skid"].to_list()
    skids = list(set([int(skid) for skid in skids]))
    return skids

def read_positions_csv(csv_path):
    """
    The csv needs to have three columns called "id", "skid", "x", "y", "z"
    """
    data = pandas.read_csv(csv_path)
    x_list = data["x"].to_list()
    y_list = data["y"].to_list()
    z_list = data["z"].to_list()
    position_ids = data["id"].to_list()
    skids = data["skid"].to_list()
    position_ids_to_skids = {id_: skid for id_, skid in zip(position_ids, skids)}
    positions = [(z,y,x) for z,y,x in zip(z_list, y_list, x_list)]
    return positions, position_ids, position_ids_to_skids

class Predict(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        skids = data['skids']
        presynaptic_locations = data['presynaptic_locations']
        synapse_ids = data['synapse_ids']
        dset = data['dset']
        service = data['service']
        user = data['user']

        if Predict.has_access(user):
            predictions = get_neurotransmitter_predictions(skids, presynaptic_locations, service, dset)

            return jsonify({
                'Input': {
                    'skids': skids,
                    'presynaptic_locations': presynaptic_locations,
                    'dset': dset,
                    'service': service,
                    'user': user
                },
                'Predictions': predictions
            })

        else:
            return "No access, Request access here"

    @staticmethod
    def has_access(user):
        registered_users = [l.strip() for l in open('users.txt', 'r').readlines()]
        user_hash = hashlib.sha512(str.encode(user)).hexdigest()
        if user_hash in registered_users:
            return True
        return False


api.add_resource(Predict, '/predict')

if __name__ == '__main__':
    app.run(debug=True)
