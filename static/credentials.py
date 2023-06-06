import getpass
from utils.init import get_access_token


username = getpass.getuser()
token_url = "https://api.korewireless.com/Api/api/token"
client_id = "CLIENT_ID"
client_secret_key = "CLIENT_SECRET"
api_key = "API_KEY"
account_id = "ACCOUNT_ID"

api_headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + get_access_token(token_url, client_id, client_secret_key)
}
