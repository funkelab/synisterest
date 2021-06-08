from synistereq.predict_neurotransmitters import predict_neurotransmitters
from synistereq.utils import read_skids_csv, read_positions_csv, format_predictions, write_predictions, log_config
from synistereq.report import generate_report
import os

service_to_dset = {"CATMAID": "FAFB",
                   "NEUPRINT": "HEMI",
                   "FLYWIRE": "FAFB",
                   "FAFB": "FAFB",
                   "HEMI": "HEMI"}

def predict(job):
    uid = job["uid"]
    request_id = job["request_id"]
    mail = job["mail"]
    service = job["service"]
    predict_from = job["predict_from"]

    csv_file = f"requests/r_{uid}_{request_id}.csv"
    position_ids_to_skids = {}
    positions = None
    position_ids = None
    skids = None
    if predict_from == "POSITION":
        positions, position_ids, position_ids_to_skids = read_positions_csv(csv_file)
    elif predict_from == "NEURON":
        skids = read_skids_csv(csv_file)
    else:
        raise ValueError(f"Cannot predict from {predict_from}")

    dset = service_to_dset[service]
    nt_probabilities, positions, \
        position_ids, position_ids_to_skids = predict_neurotransmitters(dset,
                                                                        service,
                                                                        skids,
                                                                        positions,
                                                                        position_ids,
                                                                        position_ids_to_skids,
                                                                        batch_size=8)

    print(nt_probabilities)
