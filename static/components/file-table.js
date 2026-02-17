import { h, htm, useRef } from "../lib.js";
import { formatBytes, formatDate } from "../format.js";
import * as api from "../api.js";

const html = htm.bind(h);

export function FileTable({ files, loading, onRefresh, onLoadingChange }) {
  const fileInputRef = useRef(null);
  const pendingRef = useRef(null);

  function startAdd() {
    pendingRef.current = { type: "add" };
    fileInputRef.current.value = "";
    fileInputRef.current.click();
  }

  function startReplace(fileId) {
    pendingRef.current = { type: "replace", fileId };
    fileInputRef.current.value = "";
    fileInputRef.current.click();
  }

  async function handleFileChange(e) {
    const file = e.target.files[0];
    const action = pendingRef.current;
    if (!file || !action) return;

    if (action.type === "add") {
      onLoadingChange("Uploading & indexing...");
      await api.addFile(file);
    } else if (action.type === "replace") {
      onLoadingChange("Replacing & re-indexing...");
      await api.replaceFile(action.fileId, file);
    }

    pendingRef.current = null;
    onLoadingChange(null);
    onRefresh();
  }

  async function handleDelete(fileId, filename) {
    if (!confirm(`Delete "${filename}"?`)) return;
    onLoadingChange("Deleting...");
    await api.deleteFile(fileId);
    onLoadingChange(null);
    onRefresh();
  }

  if (loading) {
    return html`<div class="loading">Loading files...</div>`;
  }

  return html`
    <div>
      <div class="toolbar">
        <h2>Files</h2>
        <button class="btn-primary" onClick=${startAdd}>Add file</button>
      </div>

      ${files.length === 0 && html`
        <div class="empty-state">
          <p>No files in this store yet.</p>
        </div>
      `}

      ${files.length > 0 && html`
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>File ID</th>
              <th>Size</th>
              <th>Status</th>
              <th>Added</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${files.map((f) => html`
              <tr key=${f.id}>
                <td><strong>${f.filename}</strong></td>
                <td class="file-id">${f.id}</td>
                <td class="file-size">${formatBytes(f.bytes)}</td>
                <td><span class="status status-${f.status}">${f.status}</span></td>
                <td class="file-size">${formatDate(f.created_at)}</td>
                <td class="actions">
                  <button onClick=${() => startReplace(f.id)}>Replace</button>
                  <button class="btn-danger" onClick=${() => handleDelete(f.id, f.filename)}>Delete</button>
                </td>
              </tr>
            `)}
          </tbody>
        </table>
      `}

      <input
        type="file"
        class="hidden-input"
        ref=${fileInputRef}
        onChange=${handleFileChange}
      />
    </div>
  `;
}
