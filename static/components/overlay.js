import { h, htm } from "../lib.js";

const html = htm.bind(h);

export function Overlay({ message }) {
  if (!message) return null;

  return html`
    <div class="overlay visible">
      <div class="overlay-content">
        <span class="spinner"></span>
        <span>${message}</span>
      </div>
    </div>
  `;
}
