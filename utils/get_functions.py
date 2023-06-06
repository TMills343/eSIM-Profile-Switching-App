import requests
from static.credentials import api_headers
from utils.init import SVCTOPROD


def get_iccid_with_active_state(account_id, eid):
    """
    Retrieves the ICCID of the subscription with an active state for the given account ID and EID.

    Args:
        account_id (str): The ID of the account.
        eid (str): The EID to filter the subscriptions.

    Returns:
        str or None: The ICCID of the subscription with an active state, or None if not found.

    Raises:
        requests.RequestException: If an error occurs while making the API request.

    """

    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/subscriptions?page-index=0&max-page-item=10&imsi=&iccid=&eid={eid}&sim-state=&msisdn="
    payload = {}
    headers = api_headers

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        subscriptions = data.get("subscriptions", [])
        for subscription in subscriptions:
            states = subscription.get("states", [])
            for state in states:
                if state.get("state") == "Active":
                    return subscription.get("iccid")

    except requests.RequestException as e:
        print(f"Error: {str(e)}")

    return None


def check_request_status(account_id, request_id):
    """
    Retrieves the status of a switch request for an eSIM profile from the Kore Wireless API.

    Args:
        account_id (str): The ID of the account associated with the switch request.
        request_id (str): The ID of the switch request.

    Returns:
        str: The status of the switch request. Possible values include:
            - "pending": The switch request is pending.
            - "processing": The switch request is being processed.
            - "completed": The switch request has been completed.
            - "failed": The switch request failed.
            - "unknown": The status of the switch request is unknown.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API request.

    """

    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/esim-profile-switch-requests/{request_id}"
    payload = {}
    headers = api_headers

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    request_status = response_json.get("switch-request-status")
    return request_status


def check_verizon(account_id, eid):
    """
    Checks the Verizon subscription status for a given account ID and EID.

    This function sends a GET request to the Kore Wireless API, retrieves the subscription
    information for the given account ID and EID, and checks whether there is an 'OmniSIM
    KVZW Downloadable' product offer with a 'Ready' state.

    Args:
        account_id (str): The account ID to check the subscription for.
        eid (str): The EID to check the subscription for.

    Returns:
        tuple: A tuple (bool, str) where:
            - The boolean is True if there is an 'OmniSIM KVZW Downloadable' product offer
              with a 'Ready' state, False if not, and None if there was an exception during the request.
            - The str is the 'subscription-id' of the 'OmniSIM KVZW Downloadable' product offer
              with a 'Ready' state if such exists, '' otherwise.

    Raises:
        requests.RequestException: If there was a problem with the GET request.
    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/subscriptions?page-index=0&max-page-item=10&imsi=&iccid=&eid={eid}&sim-state=&msisdn="
    payload = {}
    headers = api_headers

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()

        for subscription in data.get('subscriptions', []):
            product_offer = subscription.get('product-offer', '')
            states = subscription.get('states', [])

            if product_offer == 'OmniSIM KVZW Downloadable':
                for state in states:
                    if state.get('state', '') == 'Ready':
                        return (True, subscription.get('subscription-id', ''))
            else:
                return (False, '')

    except requests.RequestException as e:
        print(f"Error: {str(e)}")

    return (None, '')


def check_att(account_id, eid):
    """
    Checks the ATT subscription status for a given account ID and EID.

    This function sends a GET request to the Kore Wireless API, retrieves the subscription
    information for the given account ID and EID, and checks whether there is an 'OmniSIM KATTCC Downloadable'
    product offer with a 'Ready' state.

    Args:
        account_id (str): The account ID to check the subscription for.
        eid (str): The EID to check the subscription for.

    Returns:
        tuple: A tuple (bool, str) where:
            - The boolean is True if there is an 'OmniSIM KATTCC Downloadable' product offer
              with a 'Ready' state, False if not, and None if there was an exception during the request.
            - The str is the 'subscription-id' of the 'OmniSIM KATTCC Downloadable' product offer
              with a 'Ready' state if such exists, '' otherwise.

    Raises:
        requests.RequestException: If there was a problem with the GET request.
    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/subscriptions?page-index=0&max-page-item=10&imsi=&iccid=&eid={eid}&sim-state=&msisdn="
    payload = {}
    headers = api_headers

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()

        for subscription in data.get('subscriptions', []):
            product_offer = subscription.get('product-offer', '')
            states = subscription.get('states', [])

            if product_offer == 'OmniSIM KATTCC Downloadable':
                for state in states:
                    if state.get('state', '') == 'Ready':
                        return (True, subscription.get('subscription-id', ''))
            else:
                return (False, '')

    except requests.RequestException as e:
        print(f"Error: {str(e)}")

    return (None, '')


def check_provisioning_request_status(account_id, provisioning_request_id):
    """
    Checks the status of a provisioning request for a given account ID and provisioning request ID.

    This function sends a GET request to the Kore Wireless API and retrieves the status of
    the provisioning request. It will keep polling the API until the "Deactivation" key
    is present in the response or the timeout is reached.

    Args:
        account_id (str): The account ID of the provisioning request to check.
        provisioning_request_id (str): The provisioning request ID to check.

    Returns:
        str: The status of the provisioning request if the request was successful, '' otherwise.

    Raises:
        requests.RequestException: If there was a problem with the GET request.
    """
    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/provisioning-requests/{provisioning_request_id}"
    headers = api_headers

    try:
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        completion_status = data['Deactivation']['subscriptions'][0]['completion-status']
        return completion_status


    except requests.RequestException as e:
        print(f"Error: {str(e)}")
        return ''


def get_eid_information(account_id, eid):
    """Retrieves the profile information for the given account ID and EID.

    This function sends a GET request to the KORE Wireless API to retrieve the subscription details
    for a specific account ID and EID. It parses the JSON response and extracts the service type and state
    for each profile associated with the given EID, returning them as a list of tuples.

    Args:
        account_id (str): The ID of the account for which to retrieve subscription details.
        eid (str): The EID for which to retrieve subscription details.

    Returns:
        list[tuple[str, str]]: A list of tuples where each tuple represents a profile associated with the
                               given EID and contains two strings: the service type and the state of the profile.
                               Returns an empty list if no profiles are found.

    Raises:
        requests.RequestException: If an error occurs while making the API request. The exception is logged
                                  and the function returns None.

    """

    url = f"https://api.korewireless.com/connectivity/v1/accounts/{account_id}/subscriptions?page-index=0&max-page-item=10&imsi=&iccid=&eid={eid}&sim-state=&msisdn="
    payload = {}
    headers = api_headers
    profiles = []
    state = ''

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        subscriptions = data.get('subscriptions', [])
        for subscription in subscriptions:
            service_type_id = subscription.get('service-type-id')
            for i in subscription['states']:
                if i.get('is-current'):
                    state = i.get('state')
            service_type = SVCTOPROD.get(service_type_id)
            profile_details = (service_type, state)
            profiles.append(profile_details)
        return profiles

    except requests.RequestException as e:
        print(f"Error: {str(e)}")

    return None
