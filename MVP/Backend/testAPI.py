import requests
import argparse

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

def main():

    global URL

    parser = argparse.ArgumentParser(description='Weapons Detection API Test')

    parser.add_argument('url', help='API endpoint URL', type=str)
    parser.add_argument('--api_key', help='API key', type=str)
    parser.add_argument('--username', help='Username', type=str)
    parser.add_argument('--password', help='Password', type=str)
    parser.add_argument('--asset_id', help='Asset ID', type=str)

    args = parser.parse_args()

    if not args.api_key and (not args.username or not args.password):
        print('Please provide either an API key or both username and password.')
        return

    URL = args.url
    api_key = args.api_key

    if not api_key:
        # Call the authenticate function with the provided arguments
        access_token = authenticate('/api/auth/login', args.username, args.password)
        if access_token:
            # Call the create_api_key function
            api_key = create_api_key('/api/api-key', 'test_key', access_token)

    if api_key and args.asset_id:
        # Call the getAsset function
        getAsset('/api/asset', api_key, args.asset_id)


if __name__ == '__main__':
    main()