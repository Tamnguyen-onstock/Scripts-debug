# import pandas as pd
# import itertools

# # Đọc file company_reports.csv
# df = pd.read_csv('D:\onstocks\AI_project\Scripts-debug\company_reports.csv')

# # Danh sách các company_code
# COMPANY_CODES = df['company_code'].unique()

# # Tạo tất cả các tổ hợp có thể có của company_code, year, và quarter
# all_combinations = list(itertools.product(COMPANY_CODES, range(2020, 2025), range(1, 6)))
# all_combinations_df = pd.DataFrame(all_combinations, columns=['company_code', 'year', 'quarter'])

# # Tạo một cột key để so sánh
# all_combinations_df['key'] = all_combinations_df['company_code'] + '_' + all_combinations_df['year'].astype(str) + '_' + all_combinations_df['quarter'].astype(str)
# df['key'] = df['company_code'] + '_' + df['year'].astype(str) + '_' + df['quarter'].astype(str)

# # So sánh để tìm các tổ hợp bị thiếu
# missing_data = all_combinations_df[~all_combinations_df['key'].isin(df['key'])]

# # Xuất kết quả
# missing_data.to_csv('missing_data.csv', index=False, encoding='utf-8')

# # In ra một số thống kê
# print("Các công ty thiếu dữ liệu:")
# print(missing_data)

# # Thống kê cụ thể cho từng công ty (ví dụ: ACB thiếu quý 1 năm 2024)
# specific_missing = missing_data[(missing_data['company_code'] == 'ACB') & (missing_data['year'] == 2024) & (missing_data['quarter'] == 1)]
# if not specific_missing.empty:
#     print("\nACB thiếu dữ liệu cho quý 1 năm 2024")
# else:
#     print("\nACB không thiếu dữ liệu cho quý 1 năm 2024")


# import pandas as pd
# import itertools

# # Đọc file company_reports.csv
# df = pd.read_csv('D:\onstocks\AI_project\Scripts-debug\company_reports.csv')

# # Danh sách các company_code
# COMPANY_CODES = df['company_code'].unique()

# # Get unique document_year values from the dataset
# DOCUMENT_YEARS = df['document_year'].unique()

# # Tạo tất cả các tổ hợp có thể có của company_code, year, quarter, và document_year
# all_combinations = list(itertools.product(COMPANY_CODES, range(2020, 2025), range(1, 6), DOCUMENT_YEARS))
# all_combinations_df = pd.DataFrame(all_combinations, columns=['company_code', 'year', 'quarter', 'document_year'])

# # Tạo một cột key để so sánh
# all_combinations_df['key'] = (all_combinations_df['company_code'] + '_' + 
#                               all_combinations_df['year'].astype(str) + '_' + 
#                               all_combinations_df['quarter'].astype(str) + '_' + 
#                               all_combinations_df['document_year'].astype(str))

# df['key'] = (df['company_code'] + '_' + 
#              df['year'].astype(str) + '_' + 
#              df['quarter'].astype(str) + '_' + 
#              df['document_year'].astype(str))

# # So sánh để tìm các tổ hợp bị thiếu
# missing_data = all_combinations_df[~all_combinations_df['key'].isin(df['key'])]

# # Xuất kết quả
# missing_data.to_csv('missing_data.csv', index=False, encoding='utf-8')

# # In ra một số thống kê
# print("Các công ty thiếu dữ liệu:")
# print(missing_data)

# # Thống kê cụ thể cho từng công ty
# # Ví dụ: ACB thiếu quý 1 năm 2024 với document_year 2024
# specific_company = 'ACB'
# specific_year = 2024
# specific_quarter = 1
# specific_document_year = 2024

# specific_missing = missing_data[(missing_data['company_code'] == specific_company) & 
#                                (missing_data['year'] == specific_year) & 
#                                (missing_data['quarter'] == specific_quarter) &
#                                (missing_data['document_year'] == specific_document_year)]

# if not specific_missing.empty:
#     print(f"\n{specific_company} thiếu dữ liệu cho quý {specific_quarter} năm {specific_year} với document_year {specific_document_year}")
# else:
#     print(f"\n{specific_company} không thiếu dữ liệu cho quý {specific_quarter} năm {specific_year} với document_year {specific_document_year}")

# # Function to check if a specific combination is missing
# def check_missing_combination(company, year, quarter, document_year):
#     check = missing_data[(missing_data['company_code'] == company) & 
#                          (missing_data['year'] == year) & 
#                          (missing_data['quarter'] == quarter) &
#                          (missing_data['document_year'] == document_year)]
#     return not check.empty

# # Example usage
# is_missing = check_missing_combination('ACB', 2024, 1, 2024)
# print(f"Is ACB missing Q1 2024 with document_year 2024? {is_missing}")


import pandas as pd
import itertools

# Đọc file company_reports.csv
df = pd.read_csv('D:\onstocks\AI_project\Scripts-debug\company_reports.csv')

# Danh sách các company_code
COMPANY_CODES = df['company_code'].unique()

# Tạo tất cả các tổ hợp có thể có của company_code, năm (2020-2024), và quý (1-5)
all_combinations = list(itertools.product(COMPANY_CODES, range(2020, 2025), range(1, 6)))
all_combinations_df = pd.DataFrame(all_combinations, columns=['company_code', 'year', 'quarter'])

# Tạo key cho tất cả các tổ hợp cần kiểm tra
all_combinations_df['key'] = all_combinations_df['company_code'] + '_' + all_combinations_df['year'].astype(str) + '_' + all_combinations_df['quarter'].astype(str)

# Tạo key cho dữ liệu trong cột 'year'
df['year_key'] = df['company_code'] + '_' + df['year'].astype(str) + '_' + df['quarter'].astype(str)

# Tạo key cho dữ liệu trong cột 'document_year'
df['doc_year_key'] = df['company_code'] + '_' + df['document_year'].astype(str) + '_' + df['quarter'].astype(str)

# Lấy tất cả các key từ cả year và document_year
all_existing_keys = pd.concat([df['year_key'], df['doc_year_key']]).unique()

# So sánh để tìm các tổ hợp thực sự bị thiếu (không có trong cả year và document_year)
missing_data = all_combinations_df[~all_combinations_df['key'].isin(all_existing_keys)]

# Xuất kết quả
missing_data.to_csv('missing_data.csv', index=False, encoding='utf-8')

# In ra một số thống kê
print("Các công ty thiếu dữ liệu:")
print(missing_data.head())
print(f"Tổng số bản ghi bị thiếu: {len(missing_data)}")

# Thống kê cụ thể cho từng công ty
def check_missing_combination(company, year, quarter):
    # Tạo key để kiểm tra
    check_key = f"{company}_{year}_{quarter}"
    
    # Kiểm tra xem key có trong danh sách các key từ year không
    exists_in_year = check_key in df['year_key'].values
    
    # Kiểm tra xem key có trong danh sách các key từ document_year không
    exists_in_doc_year = check_key in df['doc_year_key'].values
    
    # Kiểm tra xem có thực sự bị thiếu không (không có trong cả year và document_year)
    is_missing = not (exists_in_year or exists_in_doc_year)
    
    return {
        'is_missing': is_missing,
        'exists_in_year': exists_in_year,
        'exists_in_doc_year': exists_in_doc_year
    }

# Ví dụ: Kiểm tra ACB quý 1 năm 2024
result = check_missing_combination('ACB', 2024, 1)
if result['is_missing']:
    print(f"\nACB thiếu dữ liệu cho quý 1 năm 2024 (không có trong cả year và document_year)")
else:
    if result['exists_in_year'] and result['exists_in_doc_year']:
        print(f"\nACB có dữ liệu cho quý 1 năm 2024 trong cả year và document_year")
    elif result['exists_in_year']:
        print(f"\nACB có dữ liệu cho quý 1 năm 2024 trong year nhưng không có trong document_year")
    else:
        print(f"\nACB có dữ liệu cho quý 1 năm 2024 trong document_year nhưng không có trong year")

# Thống kê tổng quan
print("\nThống kê tổng quan về dữ liệu thiếu:")
for company in COMPANY_CODES[:5]:  # Lấy 5 công ty đầu tiên làm ví dụ
    missing_count = len(missing_data[missing_data['company_code'] == company])
    print(f"{company}: thiếu {missing_count} tổ hợp dữ liệu")