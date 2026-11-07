// PDF aus kapazitaet.html erzeugen (Chromium über Playwright 1.48.2).
// docker run --rm -v <playwright-node_modules-ordner>:/s:ro -v "$PWD/docs/kapazitaet":/work \
//   mcr.microsoft.com/playwright:v1.48.2-jammy node /work/pdf.mjs
import { chromium } from '/s/node_modules/playwright/index.mjs';

const ziel = process.argv[2] || '/work/Waybuild-Analytics_Server-Auslastung_25-1000-Websites.pdf';
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage();
await p.goto('file:///work/kapazitaet.html', { waitUntil: 'load' });
await p.pdf({
  path: ziel,
  printBackground: true,
  preferCSSPageSize: true,
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate:
    '<div style="font-family:DejaVu Sans,Arial,sans-serif;font-size:7.5pt;color:#5d6b6b;width:100%;padding:0 14mm;display:flex;justify-content:space-between">' +
    '<span>Waybuild Analytics – Server-Auslastung 25 bis 1.000 Websites · Stand 07.11.2026 · Schätzung</span>' +
    '<span>Seite <span class="pageNumber"></span> von <span class="totalPages"></span></span></div>',
});
await b.close();
console.log('PDF:', ziel);
