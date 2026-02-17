import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import FastMCP

load_dotenv()

client = OpenAI()
VECTOR_STORE_ID = os.environ["VECTOR_STORE_ID"]

mcp = FastMCP(
    name="MyApp Docs MCP",
    instructions=(
        "Search and fetch MyApp documentation. "
        "Use search first, then fetch the best matching document(s)."
    ),
)

def mcp_text_payload(obj) -> dict:
    # MCP tool results should be a content array containing one text item (JSON-encoded string).
    return {"content": [{"type": "text", "text": json.dumps(obj)}]}

@mcp.tool()
async def search(query: str):
    if not query or not query.strip():
        return mcp_text_payload({"results": []})

    resp = client.vector_stores.search(vector_store_id=VECTOR_STORE_ID, query=query)

    results = []
    for item in (getattr(resp, "data", []) or []):
        file_id = getattr(item, "file_id", None)
        filename = getattr(item, "filename", "Document")

        snippet = ""
        content_list = getattr(item, "content", []) or []
        if content_list:
            first = content_list[0]
            snippet = getattr(first, "text", "") or (first.get("text", "") if isinstance(first, dict) else "")
        snippet = (snippet[:200] + "...") if len(snippet) > 200 else snippet

        if file_id:
            results.append({
                "id": file_id,
                "title": filename,
                "url": f"https://platform.openai.com/storage/files/{file_id}",
            })

    return mcp_text_payload({"results": results})

@mcp.tool()
async def fetch(id: str):
    if not id:
        return mcp_text_payload({"error": "Missing id"})

    content_resp = client.vector_stores.files.content(vector_store_id=VECTOR_STORE_ID, file_id=id)
    file_info = client.vector_stores.files.retrieve(vector_store_id=VECTOR_STORE_ID, file_id=id)

    parts = []
    for item in (getattr(content_resp, "data", []) or []):
        t = getattr(item, "text", None)
        if t:
            parts.append(t)

    full_text = "\n".join(parts)
    title = getattr(file_info, "filename", f"Document {id}")

    doc = {
        "id": id,
        "title": title,
        "text": full_text,
        "url": f"https://platform.openai.com/storage/files/{id}",
        "metadata": None,
    }
    return mcp_text_payload(doc)

if __name__ == "__main__":
    # HTTP transport exposes the MCP endpoint at http://localhost:8000/mcp
    mcp.run(transport="http", host="127.0.0.1", port=5055)