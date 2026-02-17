import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DOC_PATH = os.environ["DOC_PATH"]  # e.g. /Users/nico/dev/docs.pdf

client = OpenAI()

# 1) Upload file
with open(DOC_PATH, "rb") as f:
    uploaded = client.files.create(file=f, purpose="assistants")

file_id = uploaded.id
print("Uploaded file_id:", file_id)

# 2) Create vector store
vs = client.vector_stores.create(name="myapp_docs")
vector_store_id = vs.id
print("Vector store id:", vector_store_id)

# 3) Add file to vector store
client.vector_stores.files.create(
    vector_store_id=vector_store_id,
    file_id=file_id,
)

# 4) Poll until status is completed
while True:
    files = client.vector_stores.files.list(vector_store_id=vector_store_id)
    status = files.data[0].status if files.data else "unknown"
    print("Indexing status:", status)
    if status == "completed":
        break
    time.sleep(3)

print("\nDONE. Set this env var for the server:")
print("VECTOR_STORE_ID=" + vector_store_id)