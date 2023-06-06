import requests


SVCTOPROD = {
    "32": "OmniSIM Rush",
    "19": "OmniSIM KVZW Downloadable",
    "26": "OmniSIM KATTCC Downloadable"
}


def compare_values(active_iccid,bs_iccid):
    """
    Compares two values and returns True if they are the same, and False otherwise.

    Args:
        active_iccid: The active ICCID of the given eID.
        bs_iccid: The provided 'BS ICCID' of the given eID.

    Returns:
        bool: True if the values are the same, False otherwise.

    """
    return active_iccid == bs_iccid


def get_access_token(token_url,client_id,client_secret_key):
    """
    Retrieves an access token using client credentials from the given token URL.

    Args:
        client_id (str): The client ID for authentication.
        client_secret (str): The client secret for authentication.
        token_url (str): The URL to request the access token.

    Returns:
        str: The retrieved access token.

    Raises:
        requests.exceptions.RequestException: If the token request fails.

    """

    url = token_url
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret_key
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return access_token
    else:
        print("Token request failed with status code:", response.status_code)
        return None
