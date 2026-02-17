import time

from openai import OpenAI


def get_client():
    return OpenAI()


def get_store_info(client: OpenAI, vector_store_id: str):
    vs = client.vector_stores.retrieve(vector_store_id)
    return {"id": vs.id, "name": vs.name}


def rename_store(client: OpenAI, vector_store_id: str, name: str):
    vs = client.vector_stores.update(vector_store_id, name=name)
    return {"id": vs.id, "name": vs.name}


def list_files(client: OpenAI, vector_store_id: str):
    vs_files = client.vector_stores.files.list(vector_store_id=vector_store_id)
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


def upload_and_attach(client: OpenAI, vector_store_id: str, file):
    """Upload a file and attach it to a vector store.

    file: an open file handle (from disk) or a (filename, bytes) tuple.
    """
    uploaded = client.files.create(file=file, purpose="assistants")
    client.vector_stores.files.create(
        vector_store_id=vector_store_id, file_id=uploaded.id
    )
    wait_for_indexing(client, vector_store_id, uploaded.id)
    return uploaded.id


def delete_file(client: OpenAI, vector_store_id: str, file_id: str):
    client.vector_stores.files.delete(
        vector_store_id=vector_store_id, file_id=file_id
    )
    client.files.delete(file_id)


def replace_file(client: OpenAI, vector_store_id: str, old_file_id: str, file):
    """Delete old file and upload a replacement.

    file: an open file handle (from disk) or a (filename, bytes) tuple.
    """
    delete_file(client, vector_store_id, old_file_id)
    return upload_and_attach(client, vector_store_id, file)


def wait_for_indexing(
    client: OpenAI, vector_store_id: str, file_id: str, timeout: int = 120
):
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
