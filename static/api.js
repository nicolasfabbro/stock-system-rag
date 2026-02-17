export async function fetchStore() {
  const res = await fetch("/api/store");
  return res.json();
}

export async function renameStore(name) {
  const res = await fetch("/api/store", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return res.json();
}

export async function fetchFiles() {
  const res = await fetch("/api/files");
  return res.json();
}

export async function addFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/files", { method: "POST", body: form });
  return res.json();
}

export async function replaceFile(fileId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`/api/files/${fileId}/replace`, {
    method: "POST",
    body: form,
  });
  return res.json();
}

export async function deleteFile(fileId) {
  const res = await fetch(`/api/files/${fileId}`, { method: "DELETE" });
  return res.json();
}
