import requests
import json
import psycopg2
from datetime import datetime

# Elasticsearch config
ES_BASE_URL = "https://dev-elasticsearch.stock-gpt.ai"
SCROLL_TIME = "5m"
BATCH_SIZE = 1000

STOCK_INDICES = {
    # VN30 stocks
    'ACB': 'VN30', 'BCM': 'VN30', 'BID': 'VN30', 'BVH': 'VN30', 'CTG': 'VN30',
    'FPT': 'VN30', 'GAS': 'VN30', 'GVR': 'VN30', 'HDB': 'VN30', 'HPG': 'VN30',
    'MBB': 'VN30', 'MSN': 'VN30', 'MWG': 'VN30', 'PLX': 'VN30', 'POW': 'VN30',
    'SAB': 'VN30', 'SHB': 'VN30', 'SSB': 'VN30', 'SSI': 'VN30', 'STB': 'VN30',
    'TCB': 'VN30', 'TPB': 'VN30', 'VCB': 'VN30', 'VHM': 'VN30', 'VIB': 'VN30',
    'VIC': 'VN30', 'VJC': 'VN30', 'VNM': 'VN30', 'VPB': 'VN30', 'VRE': 'VN30',
    
    # VN100 stocks
    'AAA': 'VN100', 'ANV': 'VN100', 'ASM': 'VN100', 'BCG': 'VN100', 'BMP': 'VN100',
    'BSI': 'VN100', 'BWE': 'VN100', 'CII': 'VN100', 'CMG': 'VN100', 'CRE': 'VN100',
    'CTD': 'VN100', 'CTR': 'VN100', 'DBC': 'VN100', 'DCM': 'VN100', 'DGC': 'VN100',
    'DGW': 'VN100', 'DIG': 'VN100', 'DPM': 'VN100', 'DXG': 'VN100', 'DXS': 'VN100',
    'EIB': 'VN100', 'EVF': 'VN100', 'FRT': 'VN100', 'FTS': 'VN100', 'GEX': 'VN100',
    'GMD': 'VN100', 'HAG': 'VN100', 'HCM': 'VN100', 'HDC': 'VN100', 'HDG': 'VN100',
    'HHV': 'VN100', 'HSG': 'VN100', 'HT1': 'VN100', 'IMP': 'VN100', 'KBC': 'VN100',
    'KDC': 'VN100', 'KDH': 'VN100', 'KOS': 'VN100', 'LPB': 'VN100', 'MSB': 'VN100',
    'NKG': 'VN100', 'NLG': 'VN100', 'NT2': 'VN100', 'NVL': 'VN100', 'OCB': 'VN100',
    'PAN': 'VN100', 'PC1': 'VN100', 'PDR': 'VN100', 'PHR': 'VN100', 'PNJ': 'VN100',
    'PPC': 'VN100', 'PTB': 'VN100', 'PVD': 'VN100', 'PVT': 'VN100', 'REE': 'VN100',
    'SBT': 'VN100', 'SCS': 'VN100', 'SIP': 'VN100', 'SJS': 'VN100', 'SZC': 'VN100',
    'TCH': 'VN100', 'TLG': 'VN100', 'VCG': 'VN100', 'VCI': 'VN100', 'VGC': 'VN100',
    'VHC': 'VN100', 'VIX': 'VN100', 'VND': 'VN100', 'VPI': 'VN100', 'VSH': 'VN100'
}

# Industries list
INDUSTRIES = [
    'oil_gas',
    'basic_resources',
    'industrial_goods_services',
    'food_beverage',
    'health_care',
    'media',
    'telecommunications',
    'banks',
    'real_estate',
    'technology',
    'chemicals',
    'construction_materials',
    'automobiles_parts',
    'personal_household_goods',
    'retail',
    'travel_leisure',
    'utilities',
    'insurance',
    'finacial_services'
]

# PostgreSQL config
DB_CONFIG = {
    "dbname": "ost-warehouse",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def get_index_url(industry):
    return f"{ES_BASE_URL}/financial_company_{industry}_v4/_search"

def get_documents_for_industry(industry):
    # Initial search with scroll
    query = {
        "size": BATCH_SIZE,
        "query": {
            "match_all": {}
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{get_index_url(industry)}?scroll={SCROLL_TIME}",
        json=query,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error accessing index for industry {industry}: {response.status_code}")
        return

    response_data = response.json()
    scroll_id = response_data.get("_scroll_id")
    
    while True:
        hits = response_data.get("hits", {}).get("hits", [])
        if not hits:
            break
            
        for hit in hits:
            yield hit
            
        # Get next batch using scroll
        scroll_response = requests.post(
            f"{ES_BASE_URL}/_search/scroll",
            json={
                "scroll": SCROLL_TIME,
                "scroll_id": scroll_id
            },
            headers=headers
        )
        response_data = scroll_response.json()
        scroll_id = response_data.get("_scroll_id")

def insert_to_postgres(documents):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Get database info
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()
        
        cur.execute("SELECT current_user;")
        current_user = cur.fetchone()
        
        print("\nDatabase Connection Info:")
        print(f"Database Version: {db_version[0]}")
        print(f"Current Database: {db_name[0]}")
        print(f"Current User: {current_user[0]}")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print("Successfully connected to PostgreSQL database!\n")
        
        count = 0
        for doc in documents:
            try:
                source = doc["_source"]
                common_metadata = source.get("common_metadata", {})
                specific_metadata = source.get("specific_metadata", {})
                
                print(f"\nProcessing document {doc.get('_id')}...")
                print(f"Company code: {common_metadata.get('company_code')}")
                print(f"Company name: {common_metadata.get('company_name')}")
                company_code = common_metadata.get('company_code')
                stock_indices = STOCK_INDICES.get(company_code, 'OTHER')
                
                # Tạo một transaction mới cho mỗi document
                cur.execute("""
                    INSERT INTO elastic_data (
                        _id, _index, stock_indices,
                        content_type,
                        company_code, company_name, company_group,
                        year, quarter, source_location, report_type, language,
                        pdf_file_name,
                        is_tabular_data,
                        content,
                        content_vector
                    ) VALUES (
                        %s, %s, %s,
                        %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (_id) DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP,
                        content = EXCLUDED.content,
                        content_vector = EXCLUDED.content_vector
                """, (
                    doc.get('_id'), doc.get('_index'), stock_indices,
                    source.get("content_type"),
                    common_metadata.get('company_code'), 
                    common_metadata.get('company_name'), 
                    common_metadata.get('company_group'),
                    common_metadata.get('year'), 
                    common_metadata.get('quarter', None),
                    common_metadata.get('source_location'), 
                    common_metadata.get('report_type', None),
                    common_metadata.get('language'),
                    source.get('pdf_file_name'),
                    specific_metadata.get('is_tabular_data', False),
                    source.get('content'),
                    source.get('content_vector', [])
                ))
                
                # Commit sau mỗi lần insert thành công
                conn.commit()
                count += 1
                print(f"Successfully inserted document {doc.get('_id')}")
                
            except Exception as e:
                # Rollback transaction nếu có lỗi
                conn.rollback()
                print(f"Error inserting document {doc.get('_id')}: {str(e)}")
                print("Rolling back transaction and continuing with next document...")
                continue
            
            if count % 100 == 0:
                print(f"Processed {count} records...")
        
        print(f"\nTotal {count} records inserted successfully.")
        
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        if conn:
            conn.rollback()
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

def main():
    try:
        for industry in INDUSTRIES:
            print(f"\nProcessing industry: {industry}")
            documents = get_documents_for_industry(industry)
            insert_to_postgres(documents)
            print(f"Completed processing {industry}")
            
        print("\nAll industries processed successfully!")
        # industry = "finacial_services"
        # documents = get_documents_for_industry(industry)
        # count = 0
        # insert_to_postgres(documents)
        # print(f"Completed processing {industry}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()



# import psycopg2
# import json

# # PostgreSQL config
# DB_CONFIG = {
#     "dbname": "ost-warehouse",
#     "user": "admin",
#     "password": "admin",
#     "host": "localhost",
#     "port": "5432"
# }

# def test_insert():
#     try:
#         # Kết nối database
#         conn = psycopg2.connect(**DB_CONFIG)
#         cur = conn.cursor()
#         print("Connected to database successfully!")

#         # Dữ liệu test
#         test_doc = {
#             "_id": "test_doc_1",
#             "_index": "test_index",
#             # "_score": 1.0,
#             "_source": {
#                 "content_type": "text",
#                 "pdf_file_name": "test.pdf",
#                 "content": "This is a test content",
#                 "content_vector": [0.1, 0.2, 0.3],
#                 "common_metadata": {
#                     "company_code": "TEST",
#                     "company_name": "Test Company",
#                     "company_group": "Test Group",
#                     "year": "2024",
#                     "source_location": "test/location",
#                     "language": "vi"
#                 },
#                 "specific_metadata": {
#                     "is_tabular_data": False
#                 }
#             }
#         }

#         # In ra dữ liệu test để kiểm tra
#         print("\nTest data:")
#         print(json.dumps(test_doc, indent=2))

#         # Chuẩn bị dữ liệu cho câu INSERT
#         doc = test_doc
#         source = doc["_source"]
#         common_metadata = source.get("common_metadata", {})
#         specific_metadata = source.get("specific_metadata", {})

#         # In ra các giá trị sẽ được insert
#         insert_values = (
#             doc.get('_id'),
#             doc.get('_index'),
#             # doc.get('_score'),
#             source.get("content_type"),
#             common_metadata.get("company_code"),
#             common_metadata.get("company_name"),
#             common_metadata.get("company_group"),
#             common_metadata.get("year"),
#             common_metadata.get("source_location"),
#             common_metadata.get("language"),
#             source.get("pdf_file_name"),
#             specific_metadata.get("is_tabular_data", False),
#             source.get("content"),
#             source.get("content_vector", [])
#         )
        
#         print("\nValues to be inserted:")
#         for i, value in enumerate(insert_values):
#             print(f"{i+1}. {type(value).__name__}: {value}")

#         # Thực hiện câu INSERT
#         cur.execute("""
#             INSERT INTO elastic_data (
#                 _id, _index,
#                 content_type,
#                 company_code, company_name, company_group,
#                 year, source_location, language,
#                 pdf_file_name,
#                 is_tabular_data,
#                 content,
#                 content_vector
#             ) VALUES (
#                 %s, %s,
#                 %s,
#                 %s, %s, %s,
#                 %s, %s, %s,
#                 %s,
#                 %s,
#                 %s,
#                 %s
#             )
#             ON CONFLICT (_id) DO UPDATE SET
#                 updated_at = CURRENT_TIMESTAMP,
#                 content = EXCLUDED.content,
#                 content_vector = EXCLUDED.content_vector
#         """, insert_values)

#         # Commit thay đổi
#         conn.commit()
#         print("\nInsert successful!")

#         # Kiểm tra dữ liệu đã insert
#         cur.execute("SELECT * FROM elastic_data WHERE _id = %s", (doc.get('_id'),))
#         result = cur.fetchone()
#         print("\nInserted data:")
#         print(result)

#     except Exception as e:
#         print(f"\nError occurred:")
#         print(f"Type: {type(e).__name__}")
#         print(f"Message: {str(e)}")
#         if hasattr(e, 'pgcode'):
#             print(f"PostgreSQL Error Code: {e.pgcode}")
#         if hasattr(e, 'pgerror'):
#             print(f"PostgreSQL Error Message: {e.pgerror}")
#         conn.rollback()

#     finally:
#         if cur:
#             cur.close()
#         if conn:
#             conn.close()
#             print("\nDatabase connection closed.")

# if __name__ == "__main__":
#     test_insert()