# KORE_Profile_Switch_Test_Automation Web App

This web application demonstrates the management of eSIM profiles using the Kore Wireless ConnectivityPro API. It will perform the following tasks through a user-friendly interface:

- Retrieve an access token using client credentials.
- Look up the ICCID of a subscription with an active state.
- Compare values and check if they match.
- Initiate the download of a VZW profile using the Kore Wireless ConnectivityPro API.
- Initiate the download of a ATT profile using the Kore Wireless ConnectivityPro API.
- Terminate VZW profiles in the 'Ready' state on an eSIM.
- Terminate ATT profiles in the 'Ready' state on an eSIM.
- Query eID for profiles present on SIM and current state.
- Check the status of a switch request for an eSIM profile.
- Display the elapsed time from profile switch initiation to confirmation.

## Prerequisites

Before running the web app locally, make sure you have the following:

- Python 3.x installed on your system.
- Required Python packages installed. You can install them using pip install -r requirements.txt.
- Valid API credentials and permissions to access the Kore Wireless ConnectivityPro API.

## Getting Started

1. Clone this repository or download the code files.

2. Install the required Python packages by running the following command:

    pip install -r requirements.txt

3. Update the necessary API credentials and information in the code files.

4. Run the web app by executing the main.py file.

## Usage

Open the web app in your browser and fill out the required fields:

EID: Enter the EID value for the device.
IMEI: Enter the IMEI value for the device.
BS ICCID: Enter the Bootstrap ICCID value for the device.
Alternatively, you can upload a CSV file containing the device information.

Click on the "Begin Test" button to initiate the profile switch process.

The web app will display the progress and results of the profile switch, including the elapsed time.

The web app will allow you to download a .csv of the results.

## Additional Information

The web app utilizes the Kore Wireless ConnectivityPro API to manage eSIM profiles. For more information about the API and its capabilities, please refer to the Kore Wireless API Documentation.

Make sure to review and update the API URLs, endpoint paths, and other configuration settings in the code files to match your environment.
