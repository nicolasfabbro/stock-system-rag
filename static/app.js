import { h, htm, render, useState, useEffect } from "./lib.js";
import { fetchFiles } from "./api.js";
import { StoreHeader } from "./components/store-header.js";
import { FileTable } from "./components/file-table.js";
import { Overlay } from "./components/overlay.js";

const html = htm.bind(h);

function App() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [overlayMsg, setOverlayMsg] = useState(null);

  function loadFiles() {
    setLoading(true);
    fetchFiles().then((data) => {
      setFiles(data);
      setLoading(false);
    });
  }

  useEffect(() => {
    loadFiles();
  }, []);

  return html`
    <${StoreHeader} />
    <main>
      <${FileTable}
        files=${files}
        loading=${loading}
        onRefresh=${loadFiles}
        onLoadingChange=${setOverlayMsg}
      />
    </main>
    <${Overlay} message=${overlayMsg} />
  `;
}

render(html`<${App} />`, document.getElementById("app"));
