import requests

initial_url = "https://scholar.google.com/scholar"

query = {
    "hl": "en",
    "as_sdt": "0,5",
    "q": "machine learning chemistry",
    "oq": "",
}

headers = {
    "sec-ch-ua-full-version-list": '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.57", "Google Chrome";v="126.0.6478.57"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua-platform-version": "10.0.0",
    "sec-ch-ua-wow64": "?0",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "sec-ch-ua-arch": "x86",
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-model": "",
    "sec-fetch-user": "?1",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "upgrade-insecure-requests": "1",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=0, i",
    "referer": "https://scholar.google.com/?hl=en&as_sdt=0,5",
}

response = requests.get(initial_url, headers=headers, params=query)
print(response.status_code)
print(response.text)