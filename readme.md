# Neo4j + Open WebUI RAG

## Run
docker-compose up -d

## Services
- Neo4j: http://localhost:7474
- Open WebUI: http://localhost:3000
- backend: http://localhost:8000

## Neo4j demo
    # Tạo Law
    CREATE (l2013:Law {name:"Luật 2013", year:2013})
    CREATE (l2024:Law {name:"Luật 2024", year:2024})

    # Article 2013
    CREATE
    (a1:Article {number:"1", law_year:2013, title:"Phạm vi điều chỉnh"}),
    (a2:Article {number:"2", law_year:2013, title:"Đối tượng áp dụng"}),
    (a3:Article {number:"3", law_year:2013, title:"Giải thích từ ngữ"}),
    (a4:Article {number:"4", law_year:2013, title:"Nguyên tắc sử dụng đất"}),
    (a71:Article {number:"71", law_year:2013, title:"Cưỡng chế thu hồi đất"})

    # Article 2024
    CREATE
    (b1:Article {number:"1", law_year:2024, title:"Phạm vi điều chỉnh"}),
    (b2:Article {number:"2", law_year:2024, title:"Đối tượng áp dụng"}),
    (b3:Article {number:"3", law_year:2024, title:"Giải thích từ ngữ"}),
    (b4:Article {number:"4", law_year:2024, title:"Nguyên tắc sử dụng đất"}),
    (b71:Article {number:"71", law_year:2024, title:"Cưỡng chế thu hồi đất"})

    # Gắn Article vào Law
    MATCH (l:Law {year:2013}), (a:Article {law_year:2013})
    CREATE (l)-[:HAS_ARTICLE]->(a)

    MATCH (l:Law {year:2024}), (a:Article {law_year:2024})
    CREATE (l)-[:HAS_ARTICLE]->(a)

    # Quan hệ sửa đổi
    MATCH (a:Article {number:"1", law_year:2013}),
        (b:Article {number:"1", law_year:2024})
    CREATE (a)-[:AMENDED_BY]->(b)

    MATCH (a:Article {number:"2", law_year:2013}),
        (b:Article {number:"2", law_year:2024})
    CREATE (a)-[:AMENDED_BY]->(b)

    MATCH (a:Article {number:"71", law_year:2013}),
        (b:Article {number:"71", law_year:2024})
    CREATE (a)-[:AMENDED_BY]->(b)

## Open-webui

    # Vào User góc phải - Admin Panel - Settings - Connections - Kết nối Ollama hay Openai.
    # Vào User góc phải - Admin Panel - Settings - External tools.
        # url: http://host.docker.internal:8000
        # json: {
                "openapi": "3.0.0",
                "info": {
                    "title": "KG-RAG API",
                    "version": "1.0.0"
                },
                "paths": {
                    "/ask": {
                    "post": {
                        "operationId": "ask_question",
                        "summary": "kg-backend query",
                        "requestBody": {
                        "required": true,
                        "content": {
                            "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                "question": {
                                    "type": "string"
                                }
                                },
                                "required": [
                                "question"
                                ]
                            }
                            }
                        }
                        },
                        "responses": {
                        "200": {
                            "description": "Answer"
                        }
                        }
                    }
                    }
                }
                }
        # Header:   {
                    "Content-Type": "application/json"
                    }
        # Name: kg-backend
    # Vào User góc phải - Admin Panel - Settings - Documents - Full Context Mode
    # Vào workspace tạo model cho chatbot.
        # Chọn model.
        # prompt:
            Bạn là trợ lý pháp lý.

            Khi có dữ liệu từ tool, bạn phải sử dụng dữ liệu đó để trả lời.

            Nếu tool trả về:
            - context: quan hệ pháp lý
            - documents: nội dung điều luật

            Hãy:
            1. Dùng documents để trả lời nội dung điều luật
            2. Nếu không có dữ liệu thì nói không tìm thấy.

            Luôn trích dẫn nguồn luật.

        # Tạo Knowledge và upload tài liệu.
        # Tool: kg-backend
    # Ra trang chủ chọn tên chatbot vừa tạo.