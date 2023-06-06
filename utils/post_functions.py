import requests
import json
from static.credentials import username, api_headers


def download_vzw_profile(account_id, eid, imei):
    """
    Sends a request to download a VZW profile using the Kore Wireless ConnectivityPro API.

    Args:
        account_id (str): The ID of the account associated with the profile.
        eid (str): The EID of the device for which the profile is requested.
        imei (str): The IMEI of the device.

    Returns:
        None

    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/esim-profile-download-requests"

    payload = json.dumps({
        "download": {
            "activation-profile-id": "cmp-prov-ap-12548",
            "subscriptions": [
                {
                    "eid": eid,
                    "imei": imei
                },
            ],
            "service-type-info": {
                "aus-ipnd-info": {
                    "first-name": username,
                    "last-name": username
                }
            }
        }
    })
    headers = api_headers

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    request_id = response_json["data"]["request-id"]
    return request_id


def download_att_profile(account_id, eid):
    """
    Sends a request to download an ATT profile using the Kore Wireless ConnectivityPro API.

    Args:
        account_id (str): The ID of the account associated with the profile.
        eid (str): The EID of the device for which the profile is requested.
        imei (str): The IMEI of the device.

    Returns:
        None

    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/esim-profile-download-requests"

    payload = json.dumps({
        "download": {
            "activation-profile-id": "cmp-prov-ap-11052",
            "subscriptions": [
                {
                    "eid": eid
                },
            ],
            "service-type-info": {
                "aus-ipnd-info": {
                    "first-name": username,
                    "last-name": username
                }
            }
        }
    })
    headers = api_headers

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    request_id = response_json["data"]["request-id"]
    return request_id


def force_retry_switch_request(account_id, esim_profile_switch_request_id, eids):
    """
    Forcefully retry an eSIM profile switch request.

    This function sends a POST request to the Kore Wireless API to force a retry of an eSIM profile switch request.
    It requires the account ID, the ID of the switch request, and a list of EIDs that need to be retried.

    Args:
        account_id (str): The ID of the account associated with the switch request.
        esim_profile_switch_request_id (str): The ID of the eSIM profile switch request to retry.
        eids (List[str]): A list of EIDs to be retried.

    Returns:
        str or None: The status of the switch request if the request is successful and the response contains
        a 'status' field. Otherwise, it returns None.

    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/esim-profile-switch-requests/retry"
    headers = api_headers
    payload = {
        "esim-profile-switch-request-id": esim_profile_switch_request_id,
        "eids": eids,
        "skip-session-check": "true"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        if 'status' in data:
            return data['status']
    return None


def terminate_profile(account_id, subscription_id):
    """
    Terminates the subscription for a given account ID and subscription ID.

    This function sends a POST request to the Kore Wireless API, terminates the subscription
    for the given account ID and subscription ID, and retrieves the provisioning request ID.

    Args:
        account_id (str): The account ID of the subscription to terminate.
        subscription_id (str): The subscription ID to terminate.

    Returns:
        str: The provisioning request ID if the request was successful, '' otherwise.

    Raises:
        requests.RequestException: If there was a problem with the POST request.
    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/provisioning-requests/terminate"
    payload = json.dumps({
        "terminate": {
            "subscriptions": [
                {
                    "subscription-id": subscription_id
                }
            ]
        }
    })
    headers = api_headers

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()

        return data.get('data', {}).get('provisioning-request-id', '')

    except requests.RequestException as e:
        print(f"Error: {str(e)}")
        return ''
