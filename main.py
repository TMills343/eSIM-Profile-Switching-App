import time
import csv
from flask import Flask, render_template, request, send_file
from utils.init import compare_values
from static.credentials import account_id
from utils.get_functions import (get_iccid_with_active_state,
                                 check_request_status,
                                 check_verizon,
                                 check_provisioning_request_status,
                                 check_att,
                                 get_eid_information)
from utils.post_functions import (download_vzw_profile,
                                  force_retry_switch_request,
                                  terminate_profile,
                                  download_att_profile)


app = Flask(__name__, template_folder='templates')

Results = []
results_csv = []


@app.route('/')
def home():
    """Render the home page.

    This function handles the request to the root URL ("/") and
    responds by rendering the 'index.html' template.

    Returns:
        render_template: A Flask response object that contains the
                         rendered template string of 'index.html'.
    """
    global results_csv
    return render_template('index.html')


@app.route('/download_vzw_page')
def download_vzw_page():
    """
    Handles the routing to the 'download_vzw' page. Checks if a CSV file was uploaded,
    and renders the template accordingly.

    Returns:
        render_template: Rendered HTML template 'download_vzw.html' with 'csvFileUploaded' variable.
    """
    csvFileUploaded = 'csvFile' in request.files and request.files['csvFile'].filename != ''
    return render_template('download_vzw.html', csvFileUploaded=csvFileUploaded)


@app.route('/terminate_vzw_page')
def terminate_vzw_page():
    """
    Handles the routing to the 'terminate_vzw' page. Checks if a CSV file was uploaded,
    and renders the template accordingly.

    Returns:
        render_template: Rendered HTML template 'terminate_vzw.html' with 'csvFileUploaded' variable.
    """
    csvFileUploaded = 'csvFile' in request.files and request.files['csvFile'].filename != ''
    return render_template('terminate_vzw.html', csvFileUploaded=csvFileUploaded)


@app.route('/query_eid_page')
def query_eid_page():
    csvFileUploaded = 'csvFile' in request.files and request.files['csvFile'].filename != ''
    return render_template('query_eid.html', csvFileUploaded=csvFileUploaded)


@app.route('/download_att_page')
def download_att_page():
    """
    Handles the routing to the 'download_att' page. Checks if a CSV file was uploaded,
    and renders the template accordingly.

    Returns:
        render_template: Rendered HTML template 'download_att.html' with 'csvFileUploaded' variable.
    """
    csvFileUploaded = 'csvFile' in request.files and request.files['csvFile'].filename != ''
    return render_template('download_att.html', csvFileUploaded=csvFileUploaded)


@app.route('/terminate_att_page')
def terminate_att_page():
    """
    Handles the routing to the 'terminate_att' page. Checks if a CSV file was uploaded,
    and renders the template accordingly.

    Returns:
        render_template: Rendered HTML template 'terminate_att.html' with 'csvFileUploaded' variable.
    """
    csvFileUploaded = 'csvFile' in request.files and request.files['csvFile'].filename != ''
    return render_template('terminate_att.html', csvFileUploaded=csvFileUploaded)


@app.route('/download_vzw', methods=['POST'])
def download_vzw_profile_main():
    """Process the download profile request.

    This function handles the POST request to the '/download_vzw' URL.
    It accepts either a file upload containing CSV data or form data.
    It processes each row in the CSV or the form data, checking the
    active ICCID against the provided bootstrap ICCID and initiates a
    profile download if they match.

    In case of a CSV file, it's expected to contain columns with the
    names 'eid', 'imei', and 'bs_iccid' in the 4th, 2nd, and 5th
    positions respectively (0-indexed).

    In case of form data, it's expected to contain fields named 'eid',
    'imei', and 'bs_iccid'.

    Returns:
        render_template: A Flask response object that contains the
                         rendered template string of 'index.html',
                         along with the results of the profile
                         download attempts.

        results.csv: A button will be displayed to download the results
                     of the profile switching as a csv.
    """
    global results_csv
    results_csv.clear()
    Results.clear()
    if 'csvFile' in request.files:
        csv_file = request.files['csvFile']
        if csv_file.filename.endswith('.csv'):
            csv_data = csv_file.read().decode('utf-8')
            reader = csv.reader(csv_data.splitlines())
            next(reader)
            for row in reader:
                eid = row[4]
                imei = row[2]
                bs_iccid = row[5]

                active_iccid = get_iccid_with_active_state(account_id, eid)
                is_bootstrap = compare_values(active_iccid, bs_iccid)
                has_verizon, subscription_id = check_verizon(account_id, eid)

                if is_bootstrap and not has_verizon:
                    start_time = time.time()
                    request_id = download_vzw_profile(account_id, eid, imei)
                    time.sleep(1)
                    force_retry_switch_request(account_id, request_id, eid)
                    status = check_request_status(account_id, request_id)
                    while status.lower() != "completed":
                        time.sleep(1)
                        status = check_request_status(account_id, request_id)
                        if status.lower() == "failed":
                            Results.append(f"Profile download for EID: {eid} has failed.")
                            break
                    Results.append(f"Profile downloaded for EID: {eid}")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    Results.append(f"Elapsed Time: {elapsed_time} seconds")
                    results_csv.append({
                        'request_id': request_id,
                        'status': status,
                        'elapsed_time': elapsed_time
                    })
                else:
                    if has_verizon:
                        Results.append(f"EID {eid} has a Verizon profile in the Ready state. "
                                       f"Terminate the profile and try again.")
                    if not is_bootstrap:
                        Results.append(f"EID {eid} does not match the provided Bootstrap ICCID.")

            with open('results.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
                writer.writeheader()
                writer.writerows(results_csv)

            return render_template('download_vzw.html', Results=Results)

    eid = request.form['eid']
    imei = request.form['imei']
    bs_iccid = request.form['bs_iccid']

    active_iccid = get_iccid_with_active_state(account_id, eid)
    is_bootstrap = compare_values(active_iccid, bs_iccid)
    has_verizon, subscription_id = check_verizon(account_id, eid)

    if is_bootstrap and not has_verizon:
        start_time = time.time()
        request_id = download_vzw_profile(account_id, eid, imei)
        time.sleep(1)
        force_retry_switch_request(account_id,request_id,eid)
        status = check_request_status(account_id, request_id)
        while status.lower() != "completed":
            time.sleep(1)
            status = check_request_status(account_id, request_id)

            if status.lower() == "failed":
                Results.append(f"Profile download for EID: {eid} has failed.")
                break
        Results.append(f"Profile downloaded for EID: {eid}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        Results.append(f"Elapsed Time: {elapsed_time} seconds")
        results_csv.append({
            'request_id': request_id,
            'status': status,
            'elapsed_time': elapsed_time
        })
    else:
        if has_verizon:
            Results.append(f"EID {eid} has a Verizon profile in the Ready state. "
                           f"Terminate the profile and try again.")
        if not is_bootstrap:
            Results.append(f"EID {eid} does not match the provided Bootstrap ICCID.")

    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
        writer.writeheader()
        writer.writerows(results_csv)

    return render_template('download_vzw.html', Results=Results)


@app.route('/download_att', methods=['POST'])
def download_att_profile_main():
    """Process the download profile request.

    This function handles the POST request to the '/download_att' URL.
    It accepts either a file upload containing CSV data or form data.
    It processes each row in the CSV or the form data, checking the
    active ICCID against the provided bootstrap ICCID and initiates a
    profile download if they match.

    In case of a CSV file, it's expected to contain columns with the
    names 'eid', 'imei', and 'bs_iccid' in the 4th, 2nd, and 5th
    positions respectively (0-indexed).

    In case of form data, it's expected to contain fields named 'eid',
    'imei', and 'bs_iccid'.

    Returns:
        render_template: A Flask response object that contains the
                         rendered template string of 'index.html',
                         along with the results of the profile
                         download attempts.

        results.csv: A button will be displayed to download the results
                     of the profile switching as a csv.
    """
    global results_csv
    results_csv.clear()
    Results.clear()
    if 'csvFile' in request.files:
        csv_file = request.files['csvFile']
        if csv_file.filename.endswith('.csv'):
            csv_data = csv_file.read().decode('utf-8')
            reader = csv.reader(csv_data.splitlines())
            next(reader)
            for row in reader:
                eid = row[4]
                imei = row[2]
                bs_iccid = row[5]

                active_iccid = get_iccid_with_active_state(account_id, eid)
                is_bootstrap = compare_values(active_iccid, bs_iccid)
                has_att, subscription_id = check_att(account_id, eid)

                if is_bootstrap and not has_att:
                    start_time = time.time()
                    request_id = download_att_profile(account_id, eid)
                    time.sleep(1)
                    force_retry_switch_request(account_id, request_id, eid)
                    status = check_request_status(account_id, request_id)
                    while status.lower() != "completed":
                        time.sleep(1)
                        status = check_request_status(account_id, request_id)
                        if status.lower() == "failed":
                            Results.append(f"Profile download for EID: {eid} has failed.")
                            break
                    Results.append(f"Profile downloaded for EID: {eid}")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    Results.append(f"Elapsed Time: {elapsed_time} seconds")
                    results_csv.append({
                        'request_id': request_id,
                        'status': status,
                        'elapsed_time': elapsed_time
                    })
                else:
                    if has_att:
                        Results.append(f"EID {eid} has an ATT profile in the Ready state. "
                                       f"Terminate the profile and try again.")
                    if not is_bootstrap:
                        Results.append(f"EID {eid} does not match the provided Bootstrap ICCID.")

            with open('results.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
                writer.writeheader()
                writer.writerows(results_csv)

            return render_template('download_att.html', Results=Results)

    eid = request.form['eid']
    imei = request.form['imei']
    bs_iccid = request.form['bs_iccid']

    active_iccid = get_iccid_with_active_state(account_id, eid)
    is_bootstrap = compare_values(active_iccid, bs_iccid)
    has_att, subscription_id = check_att(account_id, eid)

    if is_bootstrap and not has_att:
        start_time = time.time()
        request_id = download_att_profile(account_id, eid)
        time.sleep(1)
        force_retry_switch_request(account_id,request_id,eid)
        status = check_request_status(account_id, request_id)
        while status.lower() != "completed":
            time.sleep(1)
            status = check_request_status(account_id, request_id)

            if status.lower() == "failed":
                Results.append(f"Profile download for EID: {eid} has failed.")
                break
        Results.append(f"Profile downloaded for EID: {eid}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        Results.append(f"Elapsed Time: {elapsed_time} seconds")
        results_csv.append({
            'request_id': request_id,
            'status': status,
            'elapsed_time': elapsed_time
        })
    else:
        if has_att:
            Results.append(f"EID {eid} has an ATT profile in the Ready state. "
                           f"Terminate the profile and try again.")
        if not is_bootstrap:
            Results.append(f"EID {eid} does not match the provided Bootstrap ICCID.")

    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
        writer.writeheader()
        writer.writerows(results_csv)

    return render_template('download_att.html', Results=Results)


@app.route('/terminate_vzw', methods=['POST'])
def terminate_vzw_profile():
    """
    Process the terminate profile request.

    This function handles the POST request to the '/terminate_vzw' URL.
    It accepts either a file upload containing CSV data or form data.
    It processes each row in the CSV or the form data, checking the
    Verizon profile status and initiates a profile termination if it's present.

    In case of a CSV file, it's expected to contain a column with the
    name 'eid' in the 4th position (0-indexed).

    In case of form data, it's expected to contain a field named 'eid'.

    Returns:
        render_template: A Flask response object that contains the
                         rendered template string of 'terminate_vzw.html',
                         along with the results of the profile
                         termination attempts.

        results.csv: A CSV file will be created in the root directory
                     containing the results of the profile termination.
                     It contains the request_id, status, and elapsed_time
                     for each termination attempt.
    """
    global results_csv
    results_csv.clear()
    Results.clear()
    if 'csvFile' in request.files:
        csv_file = request.files['csvFile']
        if csv_file.filename.endswith('.csv'):
            csv_data = csv_file.read().decode('utf-8')
            reader = csv.reader(csv_data.splitlines())
            next(reader)
            for row in reader:
                eid = row[4]

                has_verizon, subscription_id = check_verizon(account_id, eid)

                if has_verizon:
                    start_time = time.time()
                    provisioning_request_id = terminate_profile(account_id, subscription_id)
                    time.sleep(1)
                    status = check_provisioning_request_status(account_id, provisioning_request_id)
                    while status.lower() != "completed":
                        time.sleep(1)
                        status = check_provisioning_request_status(account_id, provisioning_request_id)
                        if status.lower() == "failed":
                            Results.append(f"Profile terminate for EID: {eid} has failed.")
                            break
                    Results.append(f"Profile terminated for EID: {eid}")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    Results.append(f"Elapsed Time: {elapsed_time} seconds")
                    results_csv.append({
                        'request_id': provisioning_request_id,
                        'status': status,
                        'elapsed_time': elapsed_time
                    })
                else:
                    Results.append(f"EID {eid} does not have a Verizon profile in the Ready state present.")

            with open('results.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
                writer.writeheader()
                writer.writerows(results_csv)

            return render_template('terminate_vzw.html', Results=Results)

    eid = request.form['eid']

    has_verizon, subscription_id = check_verizon(account_id, eid)

    if has_verizon:
        start_time = time.time()
        provisioning_request_id = terminate_profile(account_id, subscription_id)
        time.sleep(1)
        status = check_provisioning_request_status(account_id, provisioning_request_id)
        while status.lower() != "completed":
            time.sleep(1)
            status = check_provisioning_request_status(account_id, provisioning_request_id)
            if status.lower() == "failed":
                Results.append(f"Profile terminate for EID: {eid} has failed.")
                break
        Results.append(f"Profile terminated for EID: {eid}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        Results.append(f"Elapsed Time: {elapsed_time} seconds")
        results_csv.append({
            'request_id': provisioning_request_id,
            'status': status,
            'elapsed_time': elapsed_time
        })
    else:
        Results.append(f"EID {eid} does not have a Verizon profile in the Ready state present.")

    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
        writer.writeheader()
        writer.writerows(results_csv)

    return render_template('terminate_vzw.html', Results=Results)


@app.route('/terminate_att', methods=['POST'])
def terminate_att_profile():
    """
    Process the terminate profile request.

    This function handles the POST request to the '/terminate_att' URL.
    It accepts either a file upload containing CSV data or form data.
    It processes each row in the CSV or the form data, checking the
    Verizon profile status and initiates a profile termination if it's present.

    In case of a CSV file, it's expected to contain a column with the
    name 'eid' in the 4th position (0-indexed).

    In case of form data, it's expected to contain a field named 'eid'.

    Returns:
        render_template: A Flask response object that contains the
                         rendered template string of 'terminate_att.html',
                         along with the results of the profile
                         termination attempts.

        results.csv: A CSV file will be created in the root directory
                     containing the results of the profile termination.
                     It contains the request_id, status, and elapsed_time
                     for each termination attempt.
    """
    global results_csv
    Results.clear()
    results_csv.clear()
    if 'csvFile' in request.files:
        csv_file = request.files['csvFile']
        if csv_file.filename.endswith('.csv'):
            csv_data = csv_file.read().decode('utf-8')
            reader = csv.reader(csv_data.splitlines())
            next(reader)
            for row in reader:
                eid = row[4]

                has_att, subscription_id = check_att(account_id, eid)

                if has_att:
                    start_time = time.time()
                    provisioning_request_id = terminate_profile(account_id, subscription_id)
                    time.sleep(1)
                    status = check_provisioning_request_status(account_id, provisioning_request_id)
                    while status.lower() != "completed":
                        time.sleep(1)
                        status = check_provisioning_request_status(account_id, provisioning_request_id)
                        if status.lower() == "failed":
                            Results.append(f"Profile terminate for EID: {eid} has failed.")
                            break
                    Results.append(f"Profile terminated for EID: {eid}")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    Results.append(f"Elapsed Time: {elapsed_time} seconds")
                    results_csv.append({
                        'request_id': provisioning_request_id,
                        'status': status,
                        'elapsed_time': elapsed_time
                    })
                else:
                    Results.append(f"EID {eid} does not have an ATT profile in the Ready state present.")

            with open('results.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
                writer.writeheader()
                writer.writerows(results_csv)

            return render_template('terminate_att.html', Results=Results)

    eid = request.form['eid']

    has_att, subscription_id = check_att(account_id, eid)

    if has_att:
        start_time = time.time()
        provisioning_request_id = terminate_profile(account_id, subscription_id)
        time.sleep(1)
        status = check_provisioning_request_status(account_id, provisioning_request_id)
        while status.lower() != "completed":
            time.sleep(1)
            status = check_provisioning_request_status(account_id, provisioning_request_id)
            if status.lower() == "failed":
                Results.append(f"Profile terminate for EID: {eid} has failed.")
                break
        Results.append(f"Profile terminated for EID: {eid}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        Results.append(f"Elapsed Time: {elapsed_time} seconds")
        results_csv.append({
            'request_id': provisioning_request_id,
            'status': status,
            'elapsed_time': elapsed_time
        })
    else:
        Results.append(f"EID {eid} does not have an ATT profile in the Ready state present.")

    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['request_id', 'status', 'elapsed_time'])
        writer.writeheader()
        writer.writerows(results_csv)

    return render_template('terminate_att.html', Results=Results)


@app.route('/query_eid', methods=['POST'])
def query_eid():
    """Process the query for EID profile and state.

    This function handles the POST request to the '/query_eid' URL. It accepts either a CSV file upload
    or form data, and processes the provided EID(s), retrieving the profile information for each one.

    In case of a CSV file, the file is expected to contain EIDs in the first column. For each EID,
    this function retrieves the profile types and their state using the get_eid_information function.

    In case of form data, the data is expected to contain a field named 'eid'. This function retrieves
    the profile types and their state for this EID using the get_eid_information function.

    The results are stored in a global Results list and a global results_csv list, which are both cleared
    at the start of the function.

    Returns:
        render_template: A Flask response object that contains the rendered template string of
                         'query_eid.html', along with the results of the profile query.

        results.csv: A CSV file will be generated with fields 'eid', 'profile', and 'state'. If a CSV file
                     was uploaded, it will contain the results for all EIDs in the file; if form data was
                     provided, it will contain the result for the single provided EID. The CSV file can
                     then be downloaded.
    """
    Results.clear()
    results_csv.clear()
    if 'csvFile' in request.files:
        csv_file = request.files['csvFile']
        if csv_file.filename.endswith('.csv'):
            csv_data = csv_file.read().decode('utf-8')
            reader = csv.reader(csv_data.splitlines())
            next(reader)
            Results.append("Profiles:")
            for row in reader:
                eid = row[0]
                profiles = get_eid_information(account_id, eid)
                for item in profiles:
                    eid = eid
                    profile, state = item
                    Results.append(f"{eid} - {profile}: {state}")
                    results_csv.append({
                        'eid': eid,
                        'profile': profile,
                        'state': state
                    })

            with open('results.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['eid', 'profile', 'state'])
                writer.writeheader()
                writer.writerows(results_csv)

            return render_template('query_eid.html', Results=Results)

    eid = request.form['eid']

    profiles = get_eid_information(account_id, eid)
    Results.append("Profiles:")
    for item in profiles:
        eid = eid
        profile, state = item
        Results.append(f"{eid} - {profile}: {state}")
        results_csv.append({
            'eid': eid,
            'profile': profile,
            'state': state
        })

    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['eid', 'profile', 'state'])
        writer.writeheader()
        writer.writerows(results_csv)

    return render_template('query_eid.html', Results=Results)



@app.route('/download_results')
def download_results():
    """
    Handles the routing to the 'download_results' page and initiates a file download
    of 'results.csv'.

    Returns:
        send_file: A CSV file 'results.csv' for download.
    """
    return send_file('results.csv', as_attachment=True)


if __name__ == '__main__':
    app.run()
