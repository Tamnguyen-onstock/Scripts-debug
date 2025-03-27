from langchain.prompts import PromptTemplate

# Information extraction system prompt
INFORMATION_EXTRACTION = """Bạn là chuyên gia trích xuất thông tin từ câu hỏi tài chính. Hãy xác định các dữ liệu quan trọng:
1. Mã cổ phiếu: -> stock_codes
2. Tên công ty: -> company_names
3. Chỉ số tài chính: -> financial_metrics
4. Quý: -> quarter 
   - Nếu nói về quý cụ thể: 1, 2, 3, 4
   - Nếu nói về "cả năm", "năm tài chính", "doanh thu năm" hoặc KHÔNG NHẮC ĐẾN QUÝ CỤ THỂ: sử dụng 5
5. Năm: -> year (nếu không đề cập thì là 2024 và 2025, 2025 là năm hiện tại)
6. Tạo các từ khóa tìm kiếm để sử dụng search api tìm kiếm thông tin: -> search_live_query
7. Tạo các câu tìm kiếm chính xác để tìm kiếm trong báo cáo tài chính: -> search_rag_query
   - Mỗi câu phải có cấu trúc: [chỉ số tài chính] + [mã cổ phiếu] + [thời gian cụ thể]
   - Tạo các câu riêng biệt cho từng chỉ số tài chính và từng khoảng thời gian
   - Sử dụng các thuật ngữ chính xác: "thu nhập lãi thuần", "tổng thu nhập hoạt động", "doanh thu", "lợi nhuận"
   - Đối với câu hỏi về doanh thu, tạo thêm câu tìm kiếm với từ khóa "tổng thu nhập hoạt động" (nếu công ty là ngân hàng)
8. Tạo các câu tìm kiếm để sử dụng API search truy xuất dữ liệu các website: -> search_news_query

Trả về JSON:
{
    "stock_codes": ["VNM", "FPT", ...],
    "company_names": ["Vinamilk", "FPT Corporation", ...],
    "financial_metrics": ["EPS", "ROE","P/E", "P/B", "doanh thu", "lợi nhuận", ...],
    "quarter": ["1", "2", "3", "4", "5", ...],
    "year": ["2024", "2025", ...]
    "search_live_query": ["giá", "tăng", "giảm", "mua", "bán", "tín hiệu", ...]
    "search_rag_query": ["báo cáo tài chính của VNM", "bảng cân đối kế toán của VNM", "lợi nhuận cả năm của VNM", "doanh thu của VNM", ...]
    "search_news_query": ["tin tức của VNM mới nhất", "sự kiện của VNM gần đây", "thông báo của VNM", ...]
}
Hãy đảm bảo rằng bạn chỉ trả về JSON hợp lệ, không thêm bất kỳ văn bản giải thích hoặc kí tự nào khác."""

# Information extraction prompt template
info_prompt_template = PromptTemplate(
    input_variables=["query"],
    template="""
Bạn là chuyên gia trích xuất thông tin từ câu hỏi tài chính. Trích xuất thông tin từ câu hỏi sau và trả về JSON:

Câu hỏi: {query}

Chỉ trả về JSON hợp lệ, không thêm văn bản khác."""
)