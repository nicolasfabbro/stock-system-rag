import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from store import (
    get_client,
    get_store_info,
    rename_store,
    list_files,
    upload_and_attach,
    delete_file,
    replace_file,
)

load_dotenv()

VECTOR_STORE_ID = os.environ["VECTOR_STORE_ID"]

app = FastAPI()
client = get_client()

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "ui.html").read_text()


class RenameBody(BaseModel):
    name: str


@app.get("/api/store")
async def api_get_store():
    return get_store_info(client, VECTOR_STORE_ID)


@app.patch("/api/store")
async def api_rename_store(body: RenameBody):
    return rename_store(client, VECTOR_STORE_ID, body.name)


@app.get("/api/files")
async def api_list_files():
    return list_files(client, VECTOR_STORE_ID)


@app.post("/api/files")
async def api_add_file(file: UploadFile):
    content = await file.read()
    file_id = upload_and_attach(client, VECTOR_STORE_ID, (file.filename, content))
    return {"id": file_id, "filename": file.filename, "status": "completed"}


@app.post("/api/files/{file_id}/replace")
async def api_replace_file(file_id: str, file: UploadFile):
    content = await file.read()
    new_id = replace_file(client, VECTOR_STORE_ID, file_id, (file.filename, content))
    return {"id": new_id, "filename": file.filename, "status": "completed"}


@app.delete("/api/files/{file_id}")
async def api_delete_file(file_id: str):
    delete_file(client, VECTOR_STORE_ID, file_id)
    return {"deleted": file_id}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5056)
