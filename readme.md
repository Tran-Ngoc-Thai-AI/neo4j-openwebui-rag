# 🚀 Neo4j + Open WebUI (RAG System)

Hệ thống demo **RAG (Retrieval-Augmented Generation)** sử dụng:

* **Neo4j** làm Knowledge Graph
* **Open WebUI** làm giao diện chatbot
* **Backend API** để truy vấn dữ liệu

---

## 📦 Run Project

```bash
docker-compose up -d
```

---

## 🌐 Services

| Service     | URL                   |
| ----------- | --------------------- |
| Neo4j       | http://localhost:7474 |
| Open WebUI  | http://localhost:3000 |
| Backend API | http://localhost:8000 |

---

## 🧠 Neo4j Demo Data

### 1. Tạo Law

```cypher
CREATE (l2013:Law {name:"Luật 2013", year:2013})
CREATE (l2024:Law {name:"Luật 2024", year:2024})
```

---

### 2. Tạo Articles

#### Law 2013

```cypher
CREATE
(a1:Article {number:"1", law_year:2013, title:"Phạm vi điều chỉnh"}),
(a2:Article {number:"2", law_year:2013, title:"Đối tượng áp dụng"}),
(a3:Article {number:"3", law_year:2013, title:"Giải thích từ ngữ"}),
(a4:Article {number:"4", law_year:2013, title:"Nguyên tắc sử dụng đất"}),
(a71:Article {number:"71", law_year:2013, title:"Cưỡng chế thu hồi đất"})
```

#### Law 2024

```cypher
CREATE
(b1:Article {number:"1", law_year:2024, title:"Phạm vi điều chỉnh"}),
(b2:Article {number:"2", law_year:2024, title:"Đối tượng áp dụng"}),
(b3:Article {number:"3", law_year:2024, title:"Giải thích từ ngữ"}),
(b4:Article {number:"4", law_year:2024, title:"Nguyên tắc sử dụng đất"}),
(b71:Article {number:"71", law_year:2024, title:"Cưỡng chế thu hồi đất"})
```

---

### 3. Gắn Article vào Law

```cypher
MATCH (l:Law {year:2013}), (a:Article {law_year:2013})
CREATE (l)-[:HAS_ARTICLE]->(a)

MATCH (l:Law {year:2024}), (a:Article {law_year:2024})
CREATE (l)-[:HAS_ARTICLE]->(a)
```

---

### 4. Quan hệ sửa đổi (AMENDED_BY)

```cypher
MATCH (a:Article {number:"1", law_year:2013}),
      (b:Article {number:"1", law_year:2024})
CREATE (a)-[:AMENDED_BY]->(b)

MATCH (a:Article {number:"2", law_year:2013}),
      (b:Article {number:"2", law_year:2024})
CREATE (a)-[:AMENDED_BY]->(b)

MATCH (a:Article {number:"71", law_year:2013}),
      (b:Article {number:"71", law_year:2024})
CREATE (a)-[:AMENDED_BY]->(b)
```

---

## 🤖 Open WebUI Setup

### 1. Kết nối LLM

Vào:

```
User → Admin Panel → Settings → Connections
```

* Kết nối với:

  * Ollama **hoặc**
  * OpenAI

---

### 2. Cấu hình External Tool (Backend API)

Vào:

```
User → Admin Panel → Settings → External Tools
```

#### ➤ URL

```
http://host.docker.internal:8000
```

#### ➤ OpenAPI Schema

```json
{
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
                "required": ["question"]
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
```

#### ➤ Headers

```json
{
  "Content-Type": "application/json"
}
```

#### ➤ Name

```
kg-backend
```

---

### 3. Enable Full Context Mode

```
User → Admin Panel → Settings → Documents → Full Context Mode
```

---

### 4. Tạo Chatbot Model

* Chọn model (GPT / Ollama)
* Prompt:

```text
Bạn là trợ lý pháp lý.

Khi có dữ liệu từ tool, bạn phải sử dụng dữ liệu đó để trả lời.

Nếu tool trả về:
- context: quan hệ pháp lý
- documents: nội dung điều luật

Hãy:
1. Dùng documents để trả lời nội dung điều luật
2. Nếu không có dữ liệu thì nói không tìm thấy.

Luôn trích dẫn nguồn luật.
```

---

### 5. Tạo Knowledge

* Upload tài liệu pháp lý
* Gán tool: `kg-backend`

---

### 6. Sử dụng

* Vào trang chủ
* Chọn chatbot đã tạo
* Bắt đầu hỏi đáp 🔍

---

## 🧩 Kiến trúc tổng thể

```text
User → Open WebUI → Tool (Backend API) → Neo4j → LLM → Response
```

---

## 📌 Notes

* `host.docker.internal` dùng để gọi backend từ container
* Có thể mở rộng:

  * Thêm embedding
  * Thêm vector DB
  * Hybrid search (Graph + Vector)

---

## ⭐ Future Improvements

* [ ] Add vector search (FAISS / PGVector)
* [ ] Add authentication
* [ ] Improve prompt engineering
* [ ] UI customization

---

## 👨‍💻 Author

* Neo4j + RAG Demo Project
