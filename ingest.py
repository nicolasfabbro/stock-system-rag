import argparse
import os
import sys

from dotenv import load_dotenv, set_key

from store import get_client, list_files, upload_and_attach, delete_file, replace_file

load_dotenv()

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def get_vector_store_id():
    vs_id = os.environ.get("VECTOR_STORE_ID")
    if not vs_id:
        print("VECTOR_STORE_ID not set in .env. Run 'init' first.")
        sys.exit(1)
    return vs_id


def cmd_init(args):
    client = get_client()
    existing = os.environ.get("VECTOR_STORE_ID")
    if existing:
        print(f"Vector store already exists: {existing}")
        print("Delete VECTOR_STORE_ID from .env if you want to create a new one.")
        return

    vs = client.vector_stores.create(name=args.name)
    set_key(ENV_PATH, "VECTOR_STORE_ID", vs.id)
    print(f"Created vector store: {vs.id}")
    print(f"Saved to .env")


def cmd_list(args):
    client = get_client()
    vs_id = get_vector_store_id()

    files = list_files(client, vs_id)
    if not files:
        print("No files in vector store.")
        return

    print(f"Files in vector store {vs_id}:\n")
    for f in files:
        print(f"  {f['id']}  {f['filename']}  (status: {f['status']})")


def cmd_add(args):
    client = get_client()
    vs_id = get_vector_store_id()
    file_path = args.path

    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    print(f"Adding {file_path} to vector store {vs_id}...")
    with open(file_path, "rb") as f:
        file_id = upload_and_attach(client, vs_id, f)
    print(f"Done. File ID: {file_id}")


def cmd_replace(args):
    client = get_client()
    vs_id = get_vector_store_id()

    if not os.path.isfile(args.path):
        print(f"File not found: {args.path}")
        sys.exit(1)

    print(f"Replacing {args.file_id} with {args.path}...")
    with open(args.path, "rb") as f:
        file_id = replace_file(client, vs_id, args.file_id, f)
    print(f"Done. New file ID: {file_id}")


def main():
    parser = argparse.ArgumentParser(description="Manage vector store documents")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create vector store (one-time setup)")
    init_p.add_argument("--name", default="myapp_docs", help="Vector store name")

    sub.add_parser("list", help="List files in the vector store")

    add_p = sub.add_parser("add", help="Add a new file to the vector store")
    add_p.add_argument("path", help="Path to the file to upload")

    replace_p = sub.add_parser("replace", help="Replace an existing file")
    replace_p.add_argument("file_id", help="ID of the file to replace (from 'list')")
    replace_p.add_argument("path", help="Path to the new file")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "list": cmd_list,
        "add": cmd_add,
        "replace": cmd_replace,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
