from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
import requests
import re

# =================================
# CONFIG
# =================================

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

# OPENAI_URL = "http://localhost:11434/api/generate"
# OPENAI_MODEL = "qwen2.5-1.5b"



# =================================
# INIT
# =================================

app = FastAPI()

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASS)
)

class Query(BaseModel):
    question: str


# =================================
# ① INTENT DETECTION
# =================================

def detect_intent(question: str) -> str:

    q = question.lower()

    # hỏi quan hệ luật
    relation_pattern = r"(sửa đổi|sửa|thay thế|bổ sung|so sánh|khác|liên quan|mới nhất)"

    if re.search(relation_pattern, q):
        return "RELATION"

    # hỏi nội dung điều luật
    if re.search(r"điều\s*\d+", q):
        return "CONTENT"

    return "CONTENT"


# =================================
# ② EXTRACT ARTICLE ID
# =================================

def extract_article(question):

    match = re.search(r"điều\s*(\d+)", question.lower())

    if match:
        return match.group(1)

    return None


# =================================
# ③ QUERY KNOWLEDGE GRAPH
# =================================

def query_knowledge_graph(article_id):

    if not article_id:
        return []

    with driver.session() as session:

        result = session.run(
            """
            MATCH (old:Article {number:$id})-[:AMENDED_BY]->(new:Article)
            MATCH (law_old:Law)-[:HAS_ARTICLE]->(old)
            MATCH (law_new:Law)-[:HAS_ARTICLE]->(new)

            RETURN
            old.number AS old_article,
            law_old.year AS old_law,
            new.number AS new_article,
            law_new.year AS new_law
            """,
            id=article_id
        )
        print("ARTICLE:", article_id)

        data = []

        for r in result:
            data.append({
                "old_article": r["old_article"],
                "old_law": r["old_law"],
                "new_article": r["new_article"],
                "new_law": r["new_law"]
            })

        print("GRAPH RESULT:", data)
        return data


# =================================
# ④ VECTOR RETRIEVAL (DEMO)
# =================================

def get_current_article(article_id):

    with driver.session() as session:

        result = session.run(
            """
            MATCH (old:Article {number:$id})-[:AMENDED_BY]->(new:Article)
            MATCH (law_new:Law)-[:HAS_ARTICLE]->(new)
            RETURN new.number AS article, law_new.year AS year
            """,
            id=article_id
        )

        record = result.single()

        if record:
            return record["article"], record["year"]

    return article_id, None

def vector_retrieval(question, article_id):

    article_id, law_year = get_current_article(article_id)

    if law_year:

        query = f"Điều {article_id} luật đất đai {law_year}"

    else:

        query = f"Điều {article_id} luật đất đai"

    print("VECTOR QUERY:", query)

    docs = [
        {
            "source": f"Luật đất đai {law_year}",
            "content": f"Nội dung Điều {article_id} của Luật đất đai {law_year}"
        }
    ]

    return docs

def format_graph(graph_data):
    if not graph_data:
        return ""

    g = graph_data[0]

    return f"""
Điều {g['old_article']} của Luật Đất đai {g['old_law']}
được sửa đổi/thay thế bởi
Điều {g['new_article']} của Luật Đất đai {g['new_law']}.
"""

# =================================
# ⑤ CONTEXT FUSION
# =================================

# def build_context(graph_data, docs):

#     context = "=== KNOWLEDGE GRAPH ===\n"

#     if graph_data:

#         for g in graph_data:
#             context += f"""Điều {g['new_article']} sửa đổi Điều {g['old_article']}"""

#     else:
#         context += "Không tìm thấy quan hệ sửa đổi.\n"

#     context += "\n=== DOCUMENTS ===\n"

#     for d in docs:

#         context += f"""Nguồn: {d['source']}Nội dung: {d['content']}"""

#     return context


# =================================
# ⑥ CALL OPENAI
# =================================

# def call_openai(prompt):
#     payload = {
#         "model": OPENAI_MODEL,
#         "prompt": prompt,
#         "stream": False
#     }

#     res = requests.post(OPENAI_URL, json=payload)

#     print("OPENAI RAW:", res.text)   # debug

#     return res.json()["response"]


# =================================
# MAIN API
# =================================

@app.post("/ask")
def ask(query: Query):

    question = query.question

    intent = detect_intent(question)
    article_id = extract_article(question)

    if intent == "RELATION":
        graph_data = query_knowledge_graph(article_id)
        docs = vector_retrieval(question, article_id)
    else:
        graph_data = []
        docs = vector_retrieval(question, article_id)

    graph_text = format_graph(graph_data)

    return {
        "context": graph_text,
        "documents": docs
    }