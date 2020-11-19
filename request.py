import requests

res = requests.post(
    url='http://localhost:5000/predict',
    json={
        'skids': [1,16,18],
        'presynaptic_locations': [],
        'synapse_ids': [],
        'dset': "FAFB",
        'service': "CATMAID",
        'user': "nils.eckstein@googlemail.com"
    }
)

print("STATUS", res)
print("CONTENT", res.json())
