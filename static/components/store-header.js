import { h, htm, useState, useEffect } from "../lib.js";
import { fetchStore, renameStore } from "../api.js";

const html = htm.bind(h);

export function StoreHeader() {
  const [name, setName] = useState("");

  useEffect(() => {
    fetchStore().then((s) => setName(s.name));
  }, []);

  function handleClick() {
    const newName = prompt("Rename vector store:", name);
    if (!newName || newName === name) return;
    renameStore(newName).then((s) => setName(s.name));
  }

  return html`
    <header>
      <h1>Vector Store Manager</h1>
      <span class="store-name" onClick=${handleClick} title="Click to rename">
        ${name}
      </span>
    </header>
  `;
}
