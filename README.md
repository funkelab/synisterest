# SYNISTEREST
Flask based web service for neurotransmitter predictions. 

## Installation
```
conda create -n synisterest python=3.6
pip install -r requirements.txt
pip install .
```

## Start Server (Dev)
```
python app.py
```

## Package overview
This flask page allows a user to upload csv file with skids/body-ids or synapse positions. The csv file together with informations about the request, such as user id, email address and informations about the request (service to use, skids or positions) is saved in the specified requests dir (defaults to ./requests). For an example request see r_0_0.csv and r_0_0.json. The list of authorized users is saved by default in users.txt, but can be changed by adapting the relevant option in options.ini. All Flask logic is implemented in app.py. HTML templates are stored at ./templates with the bulk of the page in index.html. Static files are in ./static.

## Adding a new user
To add a new user hash the users email address and append it to the users.txt file:
```python
import hashlib

mail = lorem.ipsum@mail.com
user_hash = hashlib.sha512(str.encode(mail)).hexdigest()


## TODO
See issues.

## What should it look like?
![](design.png?raw=true)
