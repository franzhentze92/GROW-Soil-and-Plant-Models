import pprint
import requests

# Bearer token for authentication
token   = '7|XBodoDMpcDCuAtjDtlAWM78e60N1rw7mwiDyuDrH609149e9'

# Endpoint URLs
# url     = 'http://127.0.0.1:8080/api/crops/farm-management/list-farms'            # list farms
# url     = 'http://127.0.0.1:8080/api/crops/farm-management/list-paddocks'         # list paddocks
url     = 'http://127.0.0.1:8080/api/crops/farm-management/token-to-user'         # list paddocks

# url     = 'https://gestion.ntsgrow.com/api/crops/farm-management/list-farms'      # list farms
# url     = 'https://gestion.ntsgrow.com/api/crops/farm-management/list-paddocks'   # list paddocks

# Headers for the request
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}
# Set the payload for the request, for listing paddocks
# payload = {
#     'id': 'All'
# }

# Optional parameters for listing farms
# params = {
#     'FarmOwner_ID': 360,         # Replace with actual FarmOwner ID
#     # 'search': 'Organic',         # Optional
#     # 'length': 5                  # Optional pagination
# }

response = requests.get(url, headers=headers) # json=payload, params=params

try:
    data = response.json()
    from pprint import pprint
    pprint(data)
except requests.exceptions.JSONDecodeError:
    print("Invalid JSON response. Raw output:")
    print(response.text)
