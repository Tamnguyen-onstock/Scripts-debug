import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime
import logging
import os

# Thiết lập logging
logging.basicConfig(filename='log/load_to_es_new.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Kết nối đến PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            dbname="ost-warehouse",  # Thay thế bằng tên database của bạn
            # dbname="local_onstock",  # Thay thế bằng tên database của bạn
            user="admin",        # Thay thế bằng username của bạn
            password="admin",    # Thay thế bằng password của bạn
            host="localhost",           # Thay thế bằng host của bạn
            port="5432"                 # Thay thế bằng port của bạn
        )
        logging.info("Connected to PostgreSQL successfully!")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        raise

# Kết nối đến Elasticsearch
def connect_to_elasticsearch():
    try:
        es = Elasticsearch(
                ["https://dev-elasticsearch.stock-gpt.ai"],
                timeout=60,  # Tăng timeout lên 30 giây
                max_retries=3,  # Số lần thử lại
                retry_on_timeout=True  # Thử lại nếu timeout
            )
        # es = Elasticsearch(["http://localhost:9200"])
        if es.ping():
            logging.info("Connected to Elasticsearch successfully!")
            return es
        else:
            logging.error("Could not connect to Elasticsearch!")
            raise Exception("Could not connect to Elasticsearch!")
    except Exception as e:
        logging.error(f"Error connecting to Elasticsearch: {e}")
        raise

# Đọc dữ liệu từ PostgreSQL
def fetch_data_from_postgres(conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT _id, _index, content_type, company_code, company_name, company_group, year, quarter, 
                   source_location, report_type, language, pdf_file_name, is_tabular_data, content, 
                   content_vector, created_at, updated_at
            FROM es_data_vn30;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logging.info(f"Fetched {len(rows)} rows from PostgreSQL.")
        return rows
    except Exception as e:
        logging.error(f"Error fetching data from PostgreSQL: {e}")
        raise
    finally:
        cursor.close()

# Chuẩn bị dữ liệu để đẩy lên Elasticsearch
def prepare_documents_for_es(rows):
    documents = []
    for row in rows:
        _id, _index, content_type, company_code, company_name, company_group, year, quarter, \
        source_location, report_type, language, pdf_file_name, is_tabular_data, content, \
        content_vector, created_at, updated_at = row

        document = {
            "_op_type": "create",
            "_index": f"{_index}",
            "_id": _id,
            "_source": {
                "content_type": content_type,
                "common_metadata": {
                    "company_code": company_code,
                    "company_name": company_name,
                    "company_group": company_group,
                    "year": year,
                    "quarter": quarter,
                    "source_location": source_location,
                    "report_type": report_type,
                    "language": language
                },
                "pdf_file_name": pdf_file_name,
                "specific_metadata": {
                    "is_tabular_data": is_tabular_data
                },
                "content": content,
                "document_year": year,
                "content_vector": content_vector,
                "created_at": created_at.isoformat() if created_at else datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }
        documents.append(document)
    logging.info(f"Prepared {len(documents)} documents for Elasticsearch.")
    return documents

def create_index_if_not_exists(es, index_name, stopwords):
    if not es.indices.exists(index=index_name):
        index_body = {
            "mappings": {
                "properties": {
                    "content_type": {"type": "keyword"},
                    "common_metadata": {
                        "type": "object",
                        "properties": {
                            "company_code": {"type": "keyword"},
                            "company_name": {"type": "keyword"},
                            "company_group": {"type": "keyword"},
                            "year": {"type": "integer"},
                            "quarter": {"type": "integer"},
                            "source": {"type": "keyword"},
                            "source_location": {"type": "keyword"},
                            "report_type": {"type": "keyword"},
                            "language": {"type": "keyword"}
                        }
                    },
                    "pdf_file_name": {"type": "text", "index": True},
                    "specific_metadata": {
                        "type": "object",
                        "properties": {
                            "is_tabular_data": {"type": "boolean"}
                        }
                    },
                    "document_year": {"type": "keyword"},
                    "content": {"type": "text", "index": True},
                    "content_vector": {
                        "type": "dense_vector",
                        "dims": 1024,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "index": {
                    "similarity": {
                        "default": {"type": "BM25", "b": 0.9, "k1": 0.8}
                    }
                },
                "analysis": {
                    "analyzer": {
                        "my_vi_analyzer": {
                            "type": "vi_analyzer",
                            "keep_punctuation": True,
                            "stopwords": stopwords
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)
        logging.info(f"Created index: {index_name}")
    else:
        logging.info(f"Index {index_name} already exists.")

def load_stopwords(file_path = 'stopwords.txt'):
  
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]
# Đẩy dữ liệu lên Elasticsearch
def push_to_elasticsearch(es, documents):
    try:
        # Thực hiện bulk insert
        success, failed = bulk(es, documents)

        # Log số lượng document thành công
        logging.info(f"Successfully indexed {success} documents.")

        # Log chi tiết các document bị lỗi
        if failed:
            logging.error(f"Failed to index {len(failed)} documents.")
            for item in failed:
                # Lấy thông tin chi tiết về document bị lỗi
                error_type = item.get("create", {}).get("error", {}).get("type", "Unknown error")
                error_reason = item.get("create", {}).get("error", {}).get("reason", "Unknown reason")
                document_id = item.get("create", {}).get("_id", "Unknown ID")
                document_index = item.get("create", {}).get("_index", "Unknown index")

                # Log thông tin lỗi
                logging.error(
                    f"Failed document - ID: {document_id}, Index: {document_index}, "
                    f"Error Type: {error_type}, Reason: {error_reason}"
                )
    except Exception as e:
        logging.error(f"Error pushing data to Elasticsearch: {e}")
        raise

# Hàm chính
def main():
    try:
        # # Kết nối đến PostgreSQL
        # conn = connect_to_postgres()

        # # Đọc dữ liệu từ PostgreSQL
        # rows = fetch_data_from_postgres(conn)
        # logging.info("Data fetched successfully!")

        # # Chuẩn bị dữ liệu để đẩy lên Elasticsearch
        # documents = prepare_documents_for_es(rows)
        # logging.info("Data prepared successfully!")

        # Kết nối đến Elasticsearch
        es = connect_to_elasticsearch()
        logging.info("Connected to Elasticsearch successfully!")

        # # Lấy danh sách các index duy nhất từ dữ liệu
        # unique_indices = set(doc["_index"] for doc in documents)

        stopwords = load_stopwords()
        logging.info(f"Stopwords loaded successfully! {stopwords}")

        # # Tạo index nếu chưa tồn tại
        # for index_name in unique_indices:
        #     create_index_if_not_exists(es, index_name, stopwords)

        # # Đẩy dữ liệu lên Elasticsearch
        # push_to_elasticsearch(es, documents)

        # logging.info("Data loading completed successfully!")


        es_index = 'financial_company_financial_services_v4'
        # # Tạo index nếu chưa tồn tại
        # for index_name in unique_indices:
        create_index_if_not_exists(es, es_index, stopwords)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    # finally:
    #     if conn:
    #         conn.close()
    #         logging.info("PostgreSQL connection closed.")

if __name__ == "__main__":
    main()