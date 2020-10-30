import os
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from model import get_neurotransmitter_predictions

app = Flask(__name__)
api = Api(app)

class Predict(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        skids = data['skids']
        presynaptic_locations = data['presynaptic_locations']
        dset = data['dset']
        platform = data['platform']

        predictions = get_neurotransmitter_predictions(skids, presynaptic_locations, platform, dset)
        #predictions = [{synapse_id: 0, x: 0, y: 1, z: 2, prediction: {}}, {}]

        return jsonify({
            'Input': {
                'skids': skids,
                'presynaptic_locations': presynaptic_locations,
                'dset': dset,
                'platform': platform
            },
            'Predictions': predictions
        })

api.add_resource(Predict, '/predict')

if __name__ == '__main__':
    app.run(debug=True)
