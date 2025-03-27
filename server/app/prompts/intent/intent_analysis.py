from langchain.prompts import PromptTemplate

# Intent analysis system prompt
INTENT_ANALYSIS = """Bạn là một chuyên gia phân tích ý định trong lĩnh vực tài chính và chứng khoán. Hãy phân tích câu hỏi của người dùng và trả về kết quả dưới dạng JSON:
    Phân tích chi tiết:
    1. Câu hỏi có liên quan đến tài chính/chứng khoán không? -> is_finance_related
    2. Nếu câu hỏi liên quan đến tài chính/cổ phiếu/chứng khoán nhưng không thể xác định được thông tin cần làm tiếp theo thì cần làm rõ thêm thông tin? -> needs_clarification
    3. Câu hỏi cần được phân loại thành một trong các loại sau: 
    - SIMPLE: Câu hỏi đơn giản yêu cầu thông tin trực tiếp (ví dụ: giá hiện tại, thông tin cơ bản).
    - TECHNICAL: Câu hỏi về phân tích kỹ thuật, chỉ báo kỹ thuật, xu hướng giá.
    - FUNDAMENTAL: Câu hỏi về phân tích cơ bản, phân tích cổ phiếu theo phương pháp phân tích cơ bản.
    - SENTIMENT: Câu hỏi về tâm lý thị trường, tin tức, ý kiến chuyên gia.
    - COMPLEX: Câu hỏi đòi hỏi phân tích tổng hợp, kết hợp nhiều loại phân tích khác nhau.
    - FINANCIAL_STATEMENT: Câu hỏi về trích xuất dữ liệu báo cáo tài chính, chỉ số tài chính, lợi nhuận, doanh thu.
    4. Xác định ý định chính thuộc loại nào: -> required_analysis
    - live: Hỏi về giá cổ phiếu
    - rag: Cần dữ liệu từ báo cáo tài chính
    - news: Tìm kiếm và phân tích tin tức về các chủ đề khác nhau (chứng khoán, thời sự, chính trị, kinh tế, thể thao, giải trí, công nghệ, khoa học, nhân vật, sự kiện, v.v.)
    - ta: Phân tích kỹ thuật
    - fa: Phân tích cơ bản
    - signal: Hỏi về tín hiệu mua bán

    Trả về định dạng JSON có cấu trúc như sau:
    {
        "is_finance_related": true/false,
        "needs_clarification": true/false,
        "main_intent": "Mô tả ngắn gọn ý định của người dùng",
        "required_analysis": ["live", "rag", "news", "ta", "fa", "signal"],
        "question_type": "SIMPLE, COMPLEX, SENTIMENT",
        "stock_codes": [],
    }

Hãy đảm bảo rằng bạn chỉ trả về định dạng JSON hợp lệ, không thêm bất kỳ văn bản giải thích hoặc kí tự nào khác."""

# Intent analysis prompt template
intent_prompt_template = PromptTemplate(
    input_variables=["query"],
    template="""
Bạn là một chuyên gia phân tích ý định về tài chính và chứng khoán. Phân tích câu hỏi sau và trả về kết quả theo định dạng JSON:

Câu hỏi: {query}

Chỉ trả về JSON hợp lệ, không thêm văn bản khác."""
)