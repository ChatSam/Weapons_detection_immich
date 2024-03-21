import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

URL = None

def authenticate(api_endpoint, username, password):
    access_url = URL + api_endpoint
    access_token = None

    login_data = {
        'email': username,
        'password': password
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post(access_url, json=login_data, headers=headers)

    # Process the response
    if response.status_code == 201:
        print('Authentication successful')
        access_token = response.json()['accessToken']
    else:
        print('Authentication failed')

    return access_token

def create_api_key(api_endpoint, name, access_token):
    access_url = URL + api_endpoint
    api_key = None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payload = {
        'name': name
    }

    response = requests.post(access_url, headers=headers, json=payload)

    # Process the response
    if response.status_code == 201:
        print('API key created successfully')
        api_key = response.json()['secret']
    else:
        print('API key creation failed')
        exit(1)

    return api_key

def getAsset(api_endpoint, api_key, asset_id):
    access_url = URL + api_endpoint + '/' + asset_id
    asset_data = None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': api_key
    }

    response = requests.get(access_url, headers=headers)

    # Process the response
    if response.status_code == 200:
        print('Asset retrieved successfully')
        asset_data = response.json()
        # Process the asset data
        print(asset_data)
    else:
        print('Failed to retrieve asset')

    return asset_data

@app.route('/getVideo', methods=['POST'])
def get_video():
    global URL

    data = request.get_json()

    if 'url' not in data or 'username' not in data or 'password' not in data or 'asset_id' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    URL = data['url']
    username = data['username']
    password = data['password']
    asset_id = data['asset_id']

    access_token = authenticate('/api/auth/login', username, password)
    if access_token:
        api_key = create_api_key('/api/api-key', 'test_key', access_token)
        if api_key:
            asset_data = getAsset('/api/asset', api_key, asset_id)
            if asset_data:
                return jsonify(asset_data), 200

    return jsonify({'error': 'Failed to retrieve asset'}), 500

if __name__ == '__main__':
    app.run()
