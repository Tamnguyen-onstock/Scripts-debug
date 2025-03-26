# Server capabilities for MCP
SERVER_CAPABILITIES = {
    "tools": {
        "supported": True,
        "listChanged": False
    },
    "resources": {
        "supported": False
    },
    "prompts": {
        "supported": False
    }
}

# Available tools for MCP
AVAILABLE_TOOLS = [
    {
        "name": "analyze_intent",
        "description": "Phân tích ý định người dùng trong câu hỏi về chứng khoán",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi của người dùng cần phân tích"
                }
            },
            "required": ["query"]
        },
        "returns": {
            "type": "object",
            "description": "Kết quả phân tích ý định"
        }
    },
    {
        "name": "extract_information",
        "description": "Trích xuất thông tin từ câu hỏi của người dùng",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi của người dùng cần trích xuất thông tin"
                }
            },
            "required": ["query"]
        },
        "returns": {
            "type": "object",
            "description": "Thông tin đã trích xuất"
        }
    },
    {
        "name": "define_question_type",
        "description": "Xác định loại câu hỏi của người dùng",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi của người dùng cần xác định loại"
                }
            },
            "required": ["query"]
        },
        "returns": {
            "type": "object",
            "description": "Loại câu hỏi đã xác định"
        }
    }
]