from langchain.prompts import PromptTemplate

# Question type system prompt
QUESTION_TYPE = """Câu hỏi cần được phân loại thành một trong các loại sau: 
    - SIMPLE: Câu hỏi đơn giản yêu cầu thông tin trực tiếp (ví dụ: giá hiện tại, thông tin cơ bản).
    - TECHNICAL: Câu hỏi về phân tích kỹ thuật, chỉ báo kỹ thuật, xu hướng giá.
    - FUNDAMENTAL: Câu hỏi về phân tích cơ bản, phân tích cổ phiếu theo phương pháp phân tích cơ bản.
    - SENTIMENT: Câu hỏi về tâm lý thị trường, tin tức, ý kiến chuyên gia.
    - COMPLEX: Câu hỏi đòi hỏi phân tích tổng hợp, kết hợp nhiều loại phân tích khác nhau.
    - FINANCIAL_STATEMENT: Câu hỏi về trích xuất dữ liệu báo cáo tài chính, chỉ số tài chính, lợi nhuận, doanh thu.
    Trả về định dạng JSON có cấu trúc như sau:
    {
        "question_type": "SIMPLE, COMPLEX, SENTIMENT",
    }
Hãy đảm bảo rằng chỉ trả về định dạng JSON hợp lệ, không thêm bất kỳ văn bản giải thích hoặc kí tự nào khác."""

# Question type prompt template
question_type_prompt_template = PromptTemplate(
    input_variables=["query"],
    template="""
Bạn là chuyên gia phân loại câu hỏi về tài chính. Phân loại câu hỏi sau và trả về kết quả theo định dạng JSON:

Câu hỏi: {query}

Chỉ trả về JSON hợp lệ, không thêm văn bản khác."""
)