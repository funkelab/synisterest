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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')

@app.route('/no_access')
def no_access():
    return render_template('no_access.html')

@app.route('/', methods=['POST'])
def parse_form():
    uploaded_file = request.files['file']
    mail = request.form.get("email")
    service = request.form.get("service")
    predict_from = request.form.get("type")

    if not has_access(mail):
        #flash('User not recognized. Request Access.', category="error")
        flash(Markup(render_template("redirect_access.html")), category="error")

        return redirect(url_for('index'))
    else:
        print(mail, service, predict_from)
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join("requests", secure_filename(f"{mail}.csv")))
        return redirect(url_for('submitted'))

def has_access(user):
    registered_users = [l.strip() for l in open('users.txt', 'r').readlines()]
    user_hash = hashlib.sha512(str.encode(user)).hexdigest()
    if user_hash in registered_users:
        return True
    return False

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
