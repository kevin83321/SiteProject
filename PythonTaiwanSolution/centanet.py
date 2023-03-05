# Raw Question : https://www.facebook.com/groups/pythontw/posts/10162770467338438/

import os
import requests
import json
import time

def main():

    url = 'https://hk.centanet.com/findproperty/api/Transaction/Search'
    header = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkY3MkYxRDVFMThEMjRDMDc4QzUyREVFMEEzRTZEQjI3NzE2RDE0Q0RSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6Ijl5OGRYaGpTVEFlTVV0N2dvLWJiSjNGdEZNMCJ9.eyJuYmYiOjE2NzQ5NTk4OTcsImV4cCI6MTY4MjczNTg5NywiaXNzIjoiaHR0cHM6Ly9tcy5jZW50YW5ldC5jb20vbWVtYmVyIiwiYXVkIjpbImNlbnRhbmV0YXBpIiwiaHR0cHM6Ly9tcy5jZW50YW5ldC5jb20vbWVtYmVyL3Jlc291cmNlcyJdLCJjbGllbnRfaWQiOiJudXh0X2N1c3RvbV9vaWRjIiwic3ViIjoiNzhiNzU0ODMtMjc1ZS00NzE0LTgwY2QtMmJmZDE0ZTAzYTUzIiwiYXV0aF90aW1lIjoxNjc0OTU5ODk3LCJpZHAiOiJsb2NhbCIsImxvZ2luX3R5cGUiOiJBbm9ueW1vdXMiLCJqdGkiOiJGQ0U0RjYwOTQ1RDQ5N0E0OTZCRjZDOUQ5N0ZDRUVERSIsImlhdCI6MTY3NDk1OTg5Nywic2NvcGUiOlsiY2VudGFuZXRhcGkiXX0.VLUWQ_HkW9Vy7jT0a2ErVRCQmyhQqhFnHZJU5iAacAyiYPyOLGIqXe6O5cM7U0OfjUSJD8XmsLg2x7IvSQ0apoqeCGi0arL4WdpQYInrc_bA3JZfjkUnmD0ehXXII6FD-EFgOfManf_93wZsrhETTl1DsYuiXhRqySLAZMhtXehXo6GxqmeexuQXlk5G0DXRwFl3MNL3HN32uJoW67PvSwOGyi9wUN7BnGz38pSflO0kyVYY6tUXxp9K-cNuK5eY1SGBwB2BWTOOKQJ9sycmpJbb9FKYj3G44xHgkis2F_Z4AmuIOc98GdtPMzuCT90geFAi1PzbneM4M6AKSS4GUg",
        "Connection": "keep-alive",
        "Content-Length": "318",
        "Content-Type": "application/json",
        # "Cookie": "ANONYMOUS_ID_COOKIE=78b75483-275e-4714-80cd-2bfd14e03a53; ANONYMOUS_TOKEN_COOKIE=eyJhbGciOiJSUzI1NiIsImtpZCI6IkY3MkYxRDVFMThEMjRDMDc4QzUyREVFMEEzRTZEQjI3NzE2RDE0Q0RSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6Ijl5OGRYaGpTVEFlTVV0N2dvLWJiSjNGdEZNMCJ9.eyJuYmYiOjE2NzQ5NTk4OTcsImV4cCI6MTY4MjczNTg5NywiaXNzIjoiaHR0cHM6Ly9tcy5jZW50YW5ldC5jb20vbWVtYmVyIiwiYXVkIjpbImNlbnRhbmV0YXBpIiwiaHR0cHM6Ly9tcy5jZW50YW5ldC5jb20vbWVtYmVyL3Jlc291cmNlcyJdLCJjbGllbnRfaWQiOiJudXh0X2N1c3RvbV9vaWRjIiwic3ViIjoiNzhiNzU0ODMtMjc1ZS00NzE0LTgwY2QtMmJmZDE0ZTAzYTUzIiwiYXV0aF90aW1lIjoxNjc0OTU5ODk3LCJpZHAiOiJsb2NhbCIsImxvZ2luX3R5cGUiOiJBbm9ueW1vdXMiLCJqdGkiOiJGQ0U0RjYwOTQ1RDQ5N0E0OTZCRjZDOUQ5N0ZDRUVERSIsImlhdCI6MTY3NDk1OTg5Nywic2NvcGUiOlsiY2VudGFuZXRhcGkiXX0.VLUWQ_HkW9Vy7jT0a2ErVRCQmyhQqhFnHZJU5iAacAyiYPyOLGIqXe6O5cM7U0OfjUSJD8XmsLg2x7IvSQ0apoqeCGi0arL4WdpQYInrc_bA3JZfjkUnmD0ehXXII6FD-EFgOfManf_93wZsrhETTl1DsYuiXhRqySLAZMhtXehXo6GxqmeexuQXlk5G0DXRwFl3MNL3HN32uJoW67PvSwOGyi9wUN7BnGz38pSflO0kyVYY6tUXxp9K-cNuK5eY1SGBwB2BWTOOKQJ9sycmpJbb9FKYj3G44xHgkis2F_Z4AmuIOc98GdtPMzuCT90geFAi1PzbneM4M6AKSS4GUg; ga4_user_id=78b75483-275e-4714-80cd-2bfd14e03a53; ga4_anoymous=true; ROUTE_COOKIE=%2Flist%2Ftransaction%2F%25E6%2584%2589%25E6%2599%25AF%25E6%2596%25B0%25E5%259F%258E_3-DMHSZHHRHD%3Fq%3DsklnhBQdkOCzWuycBqYEw%26fbclid%3DIwAR1unvi9TngxMaXXQBxUNoMpyk-Le28VKvtiKCEQMd33S05es-fKVVwQf2o; gr_user_id=494ea5e6-bc85-4de0-ac7f-fde1b9c7c9fa; gr_session_id_986e0ca578ece71a=9bcf747b-5c3b-4168-b77a-3b75ea1c0ffa; _ga_G8G5RGTSSC=GS1.1.1674959915.1.1.1674959915.60.0.0; gr_session_id_986e0ca578ece71a_9bcf747b-5c3b-4168-b77a-3b75ea1c0ffa=true; _ga=GA1.2.407792855.1674959916; _gid=GA1.2.419485574.1674959917; isShowToolTips=true; _gcl_au=1.1.697499844.1674959917; _ga_MLE5MEFTW0=GS1.1.1674959915.1.1.1674959991.60.0.0",
        "Host": "hk.centanet.com",
        "Lang": "hk",
        "Origin": "https://hk.centanet.com",
        "Referer": "https://hk.centanet.com/findproperty/list/transaction/%E6%84%89%E6%99%AF%E6%96%B0%E5%9F%8E_3-DMHSZHHRHD?q=sklnhBQdkOCzWuycBqYEw&fbclid=IwAR1unvi9TngxMaXXQBxUNoMpyk-Le28VKvtiKCEQMd33S05es-fKVVwQf2o",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "UserID":""
    }
    payload = {
        "postType":"Both",
        "day":"Day1095",
        "sort":"InsOrRegDate",
        "order":"Descending",
        "size":0,
        "offset":0,
        "pageSource":"search",
        "bigestAndEstate":["3-DMHSZHHRHD"],
        "phaseAndEstate":[],
        "hmas":[],
        "mtrs":[],
        "primarySchoolNets":[],
        "markets":[],
        "fbclid":"IwAR1unvi9TngxMaXXQBxUNoMpyk-Le28VKvtiKCEQMd33S05es-fKVVwQf2o",
        "keyword":""
        }
    numsPerPage = 50
    res = requests.post(url, headers=header, data=json.dumps(payload))
    js = res.json()
    totalCount = js['count']
    numIters = (totalCount // numsPerPage) + 1
    fullData = []
    for i in range(numIters):
        tmpNums = numsPerPage if (i + 1) * numsPerPage < totalCount else (totalCount - i * numsPerPage)
        print(i, tmpNums)
        payload.update({"size":tmpNums})
        payload.update({"offset":i})
        resFull = requests.post(url, headers=header, data=json.dumps(payload))
        jsFull = resFull.json()
        fullData.extend(jsFull['data'])
        time.sleep(3)
    print(len(fullData))

if __name__ == '__main__':
    main()