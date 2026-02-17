import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI
import uvicorn

load_dotenv()

app = FastAPI()
client = OpenAI()

HTML_PATH = Path(__file__).parent / "ui.html"


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PATH.read_text()


@app.get("/api/stores")
async def list_stores():
    stores = client.vector_stores.list()
    results = []
    for s in stores.data:
        results.append({
            "id": s.id,
            "name": s.name,
            "file_counts": {
                "total": s.file_counts.total,
                "completed": s.file_counts.completed,
                "in_progress": s.file_counts.in_progress,
                "failed": s.file_counts.failed,
            },
            "created_at": s.created_at,
        })
    return results


@app.get("/api/stores/{store_id}/files")
async def list_files(store_id: str):
    vs_files = client.vector_stores.files.list(vector_store_id=store_id)
    results = []
    for f in vs_files.data:
        file_info = client.files.retrieve(f.id)
        results.append({
            "id": f.id,
            "filename": getattr(file_info, "filename", "unknown"),
            "status": f.status,
            "created_at": f.created_at,
            "bytes": getattr(file_info, "bytes", None),
        })
    return results


@app.post("/api/stores/{store_id}/files")
async def add_file(store_id: str, file: UploadFile):
    content = await file.read()
    uploaded = client.files.create(
        file=(file.filename, content), purpose="assistants"
    )

    client.vector_stores.files.create(
        vector_store_id=store_id, file_id=uploaded.id
    )

    _wait_for_indexing(store_id, uploaded.id)

    file_info = client.files.retrieve(uploaded.id)
    return {
        "id": uploaded.id,
        "filename": getattr(file_info, "filename", file.filename),
        "status": "completed",
    }


@app.post("/api/stores/{store_id}/files/{file_id}/replace")
async def replace_file(store_id: str, file_id: str, file: UploadFile):
    client.vector_stores.files.delete(
        vector_store_id=store_id, file_id=file_id
    )
    client.files.delete(file_id)

    content = await file.read()
    uploaded = client.files.create(
        file=(file.filename, content), purpose="assistants"
    )

    client.vector_stores.files.create(
        vector_store_id=store_id, file_id=uploaded.id
    )

    _wait_for_indexing(store_id, uploaded.id)

    file_info = client.files.retrieve(uploaded.id)
    return {
        "id": uploaded.id,
        "filename": getattr(file_info, "filename", file.filename),
        "status": "completed",
    }


@app.delete("/api/stores/{store_id}/files/{file_id}")
async def delete_file(store_id: str, file_id: str):
    client.vector_stores.files.delete(
        vector_store_id=store_id, file_id=file_id
    )
    client.files.delete(file_id)
    return {"deleted": file_id}


def _wait_for_indexing(vector_store_id: str, file_id: str, timeout: int = 120):
    start = time.time()
    while time.time() - start < timeout:
        vs_file = client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id, file_id=file_id
        )
        if vs_file.status == "completed":
            return
        if vs_file.status == "failed":
            raise Exception(f"Indexing failed for {file_id}")
        time.sleep(2)
    raise Exception(f"Indexing timed out for {file_id}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5056)
