import requests
import json
import pandas as pd

# Bảng ánh xạ ngành (industry) tới index_mapping
INDUSTRY_TO_INDEX_MAPPING = {
    'banks': 'banks',
    'basic_resources': 'basic_resources',
    'chemicals': 'chemicals',
    'construction_materials': 'construction_materials',
    'finacial_services': 'finacial_services',
    'food_beverage': 'food_beverage',
    'health_care': 'health_care',
    'industrial_goods_services': 'industrial_goods_services',
    'insurance': 'insurance',
    'oil_gas': 'oil_gas',
    'personal_household_goods': 'personal_household_goods',
    'real_estate': 'real_estate',
    'retail': 'retail',
    'technology': 'technology',
    'travel_leisure': 'travel_leisure',
    'utilities': 'utilities',
    'media': 'media',
    'telecommunications': 'telecommunications',
    'automobiles_parts': 'automobiles_parts'
}

# Bảng ánh xạ company_code tới ngành (industry)
KNOWLEDGE_VALUES_INDUSTRIES = {
    'banks': ['ACB', 'BID', 'CTG', 'EIB', 'HDB', 'LPB', 'MBB', 'MSB', 'OCB', 'SHB', 'SSB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB', 'NAB'],
    'basic_resources': ['HPG', 'HSG', 'NKG', 'PTB'],
    'chemicals': ['AAA', 'DCM', 'DGC', 'DPM', 'GVR', 'PHR'],
    'construction_materials': ['BMP', 'CII', 'CTD', 'CTR', 'HHV', 'HT1', 'PC1', 'VCG', 'VGC'],
    'finacial_services': ['BCG', 'BSI', 'EVF', 'FTS', 'HCM', 'SSI', 'VCI', 'VIX', 'VND', 'CTS', 'HVA'],
    'food_beverage': ['ANV', 'ASM', 'DBC', 'HAG', 'KDC', 'MSN', 'PAN', 'SAB', 'SBT', 'VHC', 'VNM'],
    'health_care': ['IMP'],
    'industrial_goods_services': ['GEX', 'GMD', 'PVT', 'REE', 'VTP'],
    'insurance': ['BVH'],
    'oil_gas': ['PLX', 'PVD'],
    'personal_household_goods': ['PNJ', 'TLG'],
    'real_estate': ['BCM', 'CRE', 'DIG', 'DXG', 'DXS', 'HDC', 'HDG', 'KBC', 'KDH', 'KOS', 'NLG', 'NVL', 'PDR', 'SIP', 'SJS', 'SZC', 'TCH', 'VHM', 'VIC', 'VPI', 'VRE'],
    'retail': ['DGW', 'FRT', 'MWG'],
    'technology': ['CMG', 'FPT'],
    'travel_leisure': ['SCS', 'VJC'],
    'utilities': ['BWE', 'GAS', 'NT2', 'POW', 'PPC', 'VSH'],
    'media': [],
    'telecommunications': [],
    'automobiles_parts': []
}

# Hàm để ánh xạ company_code tới index_mapping
def get_index_mapping(company_code):
    for industry, codes in KNOWLEDGE_VALUES_INDUSTRIES.items():
        if company_code in codes:
            return INDUSTRY_TO_INDEX_MAPPING.get(industry)
    return None  # Trả về None nếu không tìm thấy

# Hàm để tạo ELASTICSEARCH_URL
def get_elasticsearch_url(company_code):
    index_mapping = get_index_mapping(company_code)
    if index_mapping:
        return f"https://dev-elasticsearch.stock-gpt.ai/financial_company_{index_mapping}_v4/_search"
    else:
        raise ValueError(f"Không tìm thấy index_mapping cho company_code: {company_code}")
    
# Hàm để gửi yêu cầu tìm kiếm
def search_company_data(company_code, year, quarter):
    url = get_elasticsearch_url(company_code)
    query = {
        "size": 1000,
        "query": {
            "bool": {
                "must": [
                    {"term": {"common_metadata.company_code": company_code}},
                    {
                        "bool": {
                            "should": [
                                {"term": {"common_metadata.year": year}},
                                {"term": {"document_year": year}}
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {"term": {"common_metadata.quarter": str(quarter)}}
                ]
            }
        }
    }
    response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(query))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error searching for {company_code} in {year} Q{quarter}: {response.status_code}")
        return None

# Hàm để trích xuất và tổng hợp dữ liệu
def extract_data(search_results):
    extracted_data = []
    for hit in search_results['hits']['hits']:
        source = hit['_source']
        extracted_data.append({
            "company_code": source['common_metadata']['company_code'],
            "year": source['common_metadata']['year'],
            "document_year": source['document_year'],
            "quarter": source['common_metadata']['quarter'],
            "report_type": source['common_metadata']['report_type'],
            "pdf_file_name": source['pdf_file_name']
        })
    return extracted_data

# Tổng hợp dữ liệu từ tất cả các công ty, năm và quý
all_data = []
COMPANY_CODES = ['ACB', 'BID', 'CTG', 'EIB', 'HDB', 'LPB', 'MBB', 'MSB', 'OCB', 'SHB', 'SSB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB', 'NAB',
                 'HPG', 'HSG', 'NKG', 'PTB',
                 'AAA', 'DCM', 'DGC', 'DPM', 'GVR', 'PHR',
                 'BMP', 'CII', 'CTD', 'CTR', 'HHV', 'HT1', 'PC1', 'VCG', 'VGC',
                 'BCG', 'BSI', 'EVF', 'FTS', 'HCM', 'SSI', 'VCI', 'VIX', 'VND', 'CTS', 'HVA',
                 'ANV', 'ASM', 'DBC', 'HAG', 'KDC', 'MSN', 'PAN', 'SAB', 'SBT', 'VHC', 'VNM',
                 'IMP',
                 'GEX', 'GMD', 'PVT', 'REE', 'VTP',
                 'BVH',
                 'PLX', 'PVD',
                 'PNJ', 'TLG',
                 'BCM', 'CRE', 'DIG', 'DXG', 'DXS', 'HDC', 'HDG', 'KBC', 'KDH', 'KOS', 'NLG', 'NVL', 'PDR', 'SIP', 'SJS', 'SZC', 'TCH', 'VHM', 'VIC', 'VPI', 'VRE',
                 'DGW', 'FRT', 'MWG',
                 'CMG', 'FPT',
                 'SCS', 'VJC',
                 'BWE', 'GAS', 'NT2', 'POW', 'PPC', 'VSH'
                 ]
for company_code in COMPANY_CODES:
    for year in range(2020, 2025):  # Năm từ 2020 đến 2024
        for quarter in range(1, 6):  # Quý từ 1 đến 5
            results = search_company_data(company_code, year, quarter)
            if results and results['hits']['total']['value'] > 0:
                all_data.extend(extract_data(results))

# Chuyển dữ liệu thành DataFrame
df = pd.DataFrame(all_data)

# Lưu DataFrame thành file CSV
df.to_csv('company_reports.csv', index=False, encoding='utf-8')

# # Thống kê số lượng file theo company_code
# stats_by_company = df['company_code'].value_counts().reset_index()
# stats_by_company.columns = ['company_code', 'file_count']
# stats_by_company.to_csv('stats_by_company.csv', index=False, encoding='utf-8')

# # Thống kê số lượng file theo năm
# stats_by_year = df['year'].value_counts().reset_index()
# stats_by_year.columns = ['year', 'file_count']
# stats_by_year.to_csv('stats_by_year.csv', index=False, encoding='utf-8')

# # Thống kê số lượng file theo quý
# stats_by_quarter = df['quarter'].value_counts().reset_index()
# stats_by_quarter.columns = ['quarter', 'file_count']
# stats_by_quarter.to_csv('stats_by_quarter.csv', index=False, encoding='utf-8')

# # Thống kê số lượng file theo report_type
# stats_by_report_type = df['report_type'].value_counts().reset_index()
# stats_by_report_type.columns = ['report_type', 'file_count']
# stats_by_report_type.to_csv('stats_by_report_type.csv', index=False, encoding='utf-8')

# # In ra một số thống kê
# print("Thống kê theo công ty:")
# print(stats_by_company)

# print("\nThống kê theo năm:")
# print(stats_by_year)

# print("\nThống kê theo quý:")
# print(stats_by_quarter)

# print("\nThống kê theo loại báo cáo:")
# print(stats_by_report_type)