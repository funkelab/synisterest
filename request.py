import requests

res = requests.post(
    url='http://localhost:5000/predict',
    json={
        'skids': [1,16,18],
        'presynaptic_locations': [],
        'dset': "FAFB",
        'platform': "CATMAID"
    }
)

print("STATUS", res)
print("CONTENT", res.json())
