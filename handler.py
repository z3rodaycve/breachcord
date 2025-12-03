# Your application must self-identify via the “User-Agent” header. Failure to self-identify may result in
# revoking your API key, your license and banning your software.

import requests
import json
import time
import math
import datetime
import os
from dotenv import load_dotenv

from io import BytesIO
load_dotenv()

# Console Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def hibp_search(email: str):
    timestamp_start = time.time()
    time_now = datetime.datetime.now(datetime.UTC)

    hibp_api_key = os.getenv('HIBP_TOKEN')
    api_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
    
    headers = {
        "User-Agent": "Breachcord Developments",
        "hibp-api-key": hibp_api_key
    }

    init_search = requests.get(api_url, headers=headers, timeout=30)
    print(f"{bcolors.OKCYAN}[HAVEIBEENPWNED REQUEST]{bcolors.ENDC} Search request started with email: {email} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

    status = init_search.status_code
    
    if status == 200:
        print(f"{bcolors.OKGREEN}[HAVEIBEENPWNED REQUEST SUCCESS]{bcolors.ENDC} Search request initiated with email: {email} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")    
        init_json = json.loads(init_search.text)

        status = 1
        timestamp_end = time.time()
        
        if init_json == None:
            return {
                "status": 0
        }
        else:
            # Stealer Logs Domains
            stealer_domains = [""] 
            isStealerLog = False
            for log in init_json:
                isStealerLog = log.get("IsStealerLog", bool)
                
                if isStealerLog == True:
                    stealer_url = f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{email}"
                    stealer_request = requests.get(stealer_url, headers=headers, timeout=30)
                    stealer_json = json.loads(stealer_request.text)

                    for domain in stealer_json:
                        if domain not in stealer_domains:
                            stealer_domains.append(domain)

                    stealer_domains_json = json.dumps(stealer_domains)
                    return {
                        "result": init_json,
                        "isStealer": {"status": True},
                        "stealer_domains": stealer_domains_json,
                        "timestamp_start": timestamp_start,
                        "timestamp_end": timestamp_end
                    }
                else:
                    return {
                        "result": init_json,
                        "isStealer": {"status": False},
                        "stealer_domains": "{}",
                        "timestamp_start": timestamp_start,
                        "timestamp_end": timestamp_end
                    }
    elif status == 404:
        return {
            "status": 1
        }
        
    elif status == 400 or status == 401 or status == 403:
        print(f"{bcolors.FAIL}[HAVEIBEENPWNED REQUEST FAIL]{bcolors.ENDC} Search request failed with email: {email}, status code: {status} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
        
        return {
            "status": 2
        }

def intelx_search(domain: str, results_amount: int):
    timestamp_start = time.time()
    time_now = datetime.datetime.now(datetime.UTC)

    api_url = os.getenv('INTELX_PORTAL')
    intelx_api_key = os.getenv('INTELX_TOKEN')

    headers = {
        "User-Agent": os.getenv('INTELX_APPLICATION'),
        "x-key": intelx_api_key, # Intelx API Key
        "Content-Type": "application/json"
    }
    payload = {
        "term": domain,
        "buckets": [],
        "lookuplevel": 0,
        "maxresults": int(results_amount),
        "timeout": 0,
        "datefrom": "",
        "dateto": "",
        "sort": 2, 
        "media": 0
    }

    init_search = requests.post(api_url, headers=headers, json=payload, timeout=30)
    
    status = init_search.status_code

    if status == 200:
        print(f"{bcolors.OKCYAN}[INTELX REQUEST]{bcolors.ENDC} Search request initiated with domain: {domain} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    elif status == 400:
        print(f"{bcolors.FAIL}[INTELX REQUEST FAIL]{bcolors.ENDC} Search request failed with domain: {domain}, error: Invalid JSON | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    elif status == 401:
        print(f"{bcolors.FAIL}[INTELX UNAUTHORIZED]{bcolors.ENDC} Access not authorized. This may be due missing permission for API call or to selected buckets. | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    elif status == 402:
        print(f"{bcolors.FAIL}[INTELX TOKEN FAIL]{bcolors.ENDC} Authenticate: No credits available. No permissions to use IntelX API. | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    else:
        print(f"{bcolors.FAIL}[UNKNOWN ERROR]{bcolors.ENDC} IntelX request returned with status code of {status} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    
    init_json = init_search.json()
    selector_json = json.dumps(init_json, indent=4, ensure_ascii=False)
    unique_id = init_json.get("id", "")

    print(f"{bcolors.OKCYAN}[INTELX RESPONSE ID]{bcolors.ENDC} Search request connected with ID: {unique_id} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")


    # Result Parsing
    result_url = f"https://free.intelx.io/intelligent/search/result?id={unique_id}&offset=&limit={int(results_amount)}&previewlines="
    resp = requests.get(result_url, headers=headers, timeout=30)
    resp_json = resp.json()

    final_json = json.dumps(resp_json, indent=4, ensure_ascii=False)

    timestamp_end = time.time()

    # Status Checking
    status = resp_json.get("status", 0)
    if status == 0:
        records = resp_json.get("records", [])
        total_results = len(records)
        page_size = 1
        total_pages = max(1, math.ceil(total_results / page_size))

        return {
            "domain": domain,
            "final_json": final_json,
            "records": records,
            "total_results": total_results,
            "page_size": page_size,
            "total_pages": total_pages,
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end
        }
    else:
        return {
            "status": status,
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end
        }