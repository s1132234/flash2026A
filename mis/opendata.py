import requests, json
url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
Data = requests.get(url)
#print(Data.text)

JsonData = json.loads(Data.text)
Result = ""
for item in JsonData:
	Result += item["路口名稱"] + "：發生" + item["總件數"] + "件，主因是" + item["主要肇因"] + "\n\n"
print(Result)
