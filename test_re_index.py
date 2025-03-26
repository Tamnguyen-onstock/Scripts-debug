import requests

url = "https://dev-elasticsearch.stock-gpt.ai/_reindex"
# url = "http://localhost:9200/_reindex"
headers = {"Content-Type": "application/json"}
data = {
  "source": {
    "index": "financial_company_finacial_services_v4"
  },
  "dest": {
    "index": "financial_company_financial_services_v4"
  }
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())