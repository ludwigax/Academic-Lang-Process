import urllib.parse
import requests
import json
from copy import deepcopy

from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

INITIAL_URL = "https://webofscience.clarivate.cn/wos/alldb/basic-search"
QUERY_URL = "https://webofscience.clarivate.cn/api/wosnx/core/runQuerySearch?SID={0}"
STREAM_URL = "https://webofscience.clarivate.cn/api/wosnx/core/runQueryGetRecordsStream?SID={0}"
FULLREC_URL = "https://webofscience.clarivate.cn/api/wosnx/core/getFullRecordByQueryId?SID={0}"

EXAMPLE_HEADER = {
    "priority": "u=1, i",
    "referer": "EXAMPLE",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "accept": "application/x-ndjson",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-length": "EXAMPLE",
    "content-type": "EXAMPLE",
    "origin": "https://webofscience.clarivate.cn",
}

EXAMPLE_BODY = (
    '{"product":"ALLDB","searchMode":"general","viewType":"search","serviceMode":"summary",'
    '"search":{"mode":"general","database":"ALLDB","query":[{"rowField":"TS","rowText":"Machine learning chemistry"}],'
    '"refines":[{"index":"SILOID","value":["PPRN"],"exclude":true}]},"retrieve":{"count":50,"history":true,"jcr":true,"sort":"relevance",'
    '"analyzes":["TP.Value.6","DR.Value.6","REVIEW.Value.6","OA.Value.6","PY.Field_D.6","DT.Value.6","AU.Value.6","PEERREVIEW.Value.6"],'
    '"locale":"en_US"},"eventMode":null,"isPreprintReview":false}'
)

STREAM_BODY = (
    '{"qid":"EXAMPLE",'
    '"retrieve":{"first":"EXAMPLE","sort":"relevance","count":50,"jcr":true,"highlight":false,"analyzes":[]},'
    '"product":"ALLDB","searchMode":"general","viewType":"records"}'
)

FULLREC_BODY = (
    '{"qid":"EXAMPLE",'
    '"id":{"value":"EXAMPLE","type":"colluid"},'
    '"retrieve":{"first":1,"links":"retrieve","sort":"relevance","count":1,"view":"super","coll":"",'
    '"activity":true,"analyzes":null,"jcr":true,"reviews":true,"highlight":true,'
    '"secondaryRetrieve":{"associated_data":{"sort":"relevance","count":10},'
    '"cited_references":{"sort":"author-ascending","count":30},"citing_article":{"sort":"date","count":2,'
    '"links":null,"view":"mini"},"cited_references_with_context":{"sort":"date","count":135,"view":"mini"},'
    '"recommendation_articles":{"sort":"recommendation-relevance","count":5,"links":null,"view":"mini"},'
    '"grants_to_wos_records":{"sort":"date-descending","count":30,"links":null,"view":"mini"}},"locale":"en_US"},'
    '"product":"ALLDB","searchMode":"general","serviceMode":"summary","viewType":"records","isPreprintReview":false}'
)

kw_fields = {
    "topic": "TS",
    "author": "AU",
    "year": "PY",
    "address": "AD",
    "title": "TI",
}

# little utils
def quote(url: str):
    return urllib.parse.quote(url, safe=':/?&=')

def wos_keywords(field: str, text: str, boolean: str=None) -> Dict[str, str]:
    kwd = {
        "rowBoolean": boolean, # "AND" or "OR
        "rowField": kw_fields[field],
        "rowText": text
    }
    if boolean is None:
        kwd.pop("rowBoolean")
    return kwd

# wos scrap core function --------------------------------------------
def wos_disguise_login():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(INITIAL_URL)

    try:
        element_present = EC.presence_of_element_located((By.ID, 'specific_element_id'))
        WebDriverWait(driver, 10).until(element_present)
    except Exception as e:
        print(f"Page Loading Timeout: {e}")

    cookies = driver.get_cookies()
    for cookie in cookies:
        print(f"{cookie['name']}: {cookie['value']}")

    sid = next((cookie['value'] for cookie in cookies if cookie['name'] == 'SID'), None)
    wossid = next((cookie['value'] for cookie in cookies if cookie['name'] == 'WOSSID'), None)
    print(f"SID: {sid}")
    print(f"WOSSID: {wossid}")
    driver.quit()

    return sid, wossid

def wos_first_post(query_list: List[Dict[str, str]], sid: str):
    query_body_js = json.loads(EXAMPLE_BODY)
    query_body_js["search"]["query"] = query_list
    query_body = json.dumps(query_body_js, separators=(',', ':'))

    query_header = EXAMPLE_HEADER
    query_header["content-length"] = str(len(query_body))
    query_header["content-type"] = "text/plain;charset=UTF-8"
    query_header["referer"] = quote(INITIAL_URL)

    query_url = QUERY_URL.format(sid)
    response = requests.post(quote(query_url), headers=query_header, data=query_body)
    return response

def wos_stream_post(first: int, qid: str, sid: str):
    stream_body_js = json.loads(STREAM_BODY)
    stream_body_js["qid"] = qid
    stream_body_js["retrieve"]["first"] = str(first)
    stream_body = json.dumps(stream_body_js, separators=(',', ':'))

    stream_header = EXAMPLE_HEADER
    stream_header["content-length"] = str(len(stream_body))
    stream_header["content-type"] = "text/plain;charset=UTF-8"
    stream_header["referer"] = quote(INITIAL_URL)

    stream_url = STREAM_URL.format(sid)
    response = requests.post(quote(stream_url), headers=stream_header, data=stream_body)
    return response

def wos_fullrecord_post(wosid: str, qid: str, sid: str): # A DEMO FUNCTION
    fullrec_body_js = json.loads(FULLREC_BODY)
    fullrec_body_js["qid"] = qid
    fullrec_body_js["id"]["value"] = wosid
    fullrec_body = json.dumps(fullrec_body_js, separators=(',', ':'))

    fullrec_header = EXAMPLE_HEADER
    fullrec_header["content-length"] = str(len(fullrec_body))
    fullrec_header["content-type"] = "text/plain;charset=UTF-8"
    fullrec_header["referer"] = quote(INITIAL_URL)

    fullrec_url = FULLREC_URL.format(sid)
    response = requests.post(quote(fullrec_url), headers=fullrec_header, data=fullrec_body)
    return response

# arrange the response
def get_response(response: requests.Response, api: str="runQuerySearch", saving: bool=False):
    nddata = response.text.strip().split("\n")
    querydata = []
    queryinfo = None
    for data in nddata:
        data = json.loads(data)
        if data["key"] == "searchInfo":
            queryinfo = data

        if "api" in data and data["api"] == api:
            querydata.append(data)

    records = deepcopy(querydata[0])

    print(records["id"])
    for i in range(1, len(querydata)):
        print(querydata[i]["id"])
        payload = querydata[i].get("payload", None)
        if payload:
            records["payload"].update(payload)

    qid = queryinfo["payload"]["QueryID"]
    total_records = queryinfo["payload"]["RecordsFound"]
    n_records = len(records["payload"])

    if saving:
        svdata = {
            "qid": qid,
            "total_records": total_records,
            "n_records": n_records,
            "records": records
        }
        with open(f"catdata_{api}_{qid}.json", "w") as f:
            json.dump(svdata, f, indent=4)
    return records, qid, total_records, n_records


if __name__ == "__main__":
    sid, wossid = wos_disguise_login()

    kw = wos_keywords("topic", "Machine learning")
    kw2 = wos_keywords("topic", "BNNS", "AND")
    kw3 = wos_keywords("topic", "funcionalize", "AND")
    response = wos_first_post([kw, kw2, kw3], wossid)
    records, qid, total_records, n_records = get_response(response, "runQuerySearch", saving=True)

    for i in range(51, 100, 50):
        response = wos_stream_post(i, qid, wossid)
        records, qid, total_records, n_records = get_response(response, "runQueryGetRecordsStream", saving=True)