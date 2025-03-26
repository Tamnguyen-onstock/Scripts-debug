import pandas as pd

# Đọc dữ liệu từ file CSV
es_data = pd.read_csv('es_data.csv')
file_log = pd.read_csv('file_log.csv')

# Hàm để trích xuất tên file từ đường dẫn
def extract_filename(path):
    return path.split('/')[-1]

# Áp dụng hàm extract_filename để tạo cột mới 'filename' trong es_data
es_data['filename'] = es_data['pdf_file_name'].apply(extract_filename)

# Merge hai dataframe dựa trên cột 'filename' và 'file_name'
merged_data = pd.merge(es_data, file_log, left_on='filename', right_on='file_name', how='left')

# Điền giá trị từ cột 'quarter' và 'report_type' của file_log vào es_data
es_data['quarter'] = merged_data['quarter_y']
es_data['report_type'] = merged_data['report_type_y']

# Lưu kết quả vào file CSV mới
es_data.to_csv('es_data_updated.csv', index=False)

print("Đã cập nhật thành công vào file es_data_updated.csv")