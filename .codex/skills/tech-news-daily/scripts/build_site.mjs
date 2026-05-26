#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/";
const META_RE = /<!-- BUILD:META:START -->[\s\S]*?<!-- BUILD:META:END -->/;

function parseArgs(argv) {
  const out = { projectRoot: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--project-root") {
      out.projectRoot = argv[i + 1];
      i += 1;
    }
  }
  return out;
}

function isProjectRoot(dir) {
  return fs.existsSync(path.join(dir, "index.html")) && fs.existsSync(path.join(dir, "data"));
}

function findProjectRoot(explicit) {
  const starts = [explicit, process.env.DAILYTECHBRIEF_ROOT, process.cwd()].filter(Boolean);
  for (const start of starts) {
    let cur = path.resolve(start);
    if (fs.existsSync(cur) && fs.statSync(cur).isFile()) cur = path.dirname(cur);
    while (true) {
      if (isProjectRoot(cur)) return cur;
      const parent = path.dirname(cur);
      if (parent === cur) break;
      cur = parent;
    }
  }
  throw new Error("Project root not found. Run from the repo or pass --project-root.");
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function loadEditions(dataDir) {
  return fs
    .readdirSync(dataDir)
    .filter((name) => /^\d{4}-\d{2}-\d{2}\.json$/.test(name))
    .map((name) => JSON.parse(fs.readFileSync(path.join(dataDir, name), "utf8")))
    .sort((a, b) => b.id.localeCompare(a.id));
}

function buildMetaBlock(edition, latestId, ogUrl) {
  const dateStr = edition.id.replaceAll("-", ".");
  const title = `데일리 테크 브리프 · ${dateStr} ${edition.dayOfWeek}요일`;
  const headlines = edition.newsItems
    .slice(0, 3)
    .map((item) => `${String(item.order).padStart(2, "0")} ${item.title}`)
    .join(" · ");
  const ogImage = `${SITE_URL}date/${edition.id}/og.png`;

  return `<!-- BUILD:META:START -->
<title>${esc(title)}</title>
<meta property="og:type" content="article">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(headlines)}">
<meta property="og:image" content="${esc(ogImage)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="${esc(ogUrl)}">
<meta property="og:site_name" content="KAIST 경영대학 테크 네트워크">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(headlines)}">
<meta name="twitter:image" content="${esc(ogImage)}">
<script>
  window.__INITIAL_ID__ = "${edition.id}";
  window.__LATEST_ID__ = "${latestId}";
</script>
<!-- BUILD:META:END -->`;
}

function renderPage(template, edition, latestId, ogUrl) {
  if (!META_RE.test(template)) {
    throw new Error("Template is missing BUILD:META markers.");
  }
  return template.replace(META_RE, buildMetaBlock(edition, latestId, ogUrl));
}

const args = parseArgs(process.argv.slice(2));
const projectRoot = findProjectRoot(args.projectRoot);
const dataDir = path.join(projectRoot, "data");
const dateDir = path.join(projectRoot, "date");
const indexPath = path.join(projectRoot, "index.html");
const template = fs.readFileSync(indexPath, "utf8");
const editions = loadEditions(dataDir);

if (editions.length === 0) {
  throw new Error("No editions found in data/.");
}

const latestId = editions[0].id;
fs.mkdirSync(dateDir, { recursive: true });

for (const edition of editions) {
  const pageDir = path.join(dateDir, edition.id);
  fs.mkdirSync(pageDir, { recursive: true });
  const html = renderPage(template, edition, latestId, `${SITE_URL}date/${edition.id}/`);
  fs.writeFileSync(path.join(pageDir, "index.html"), html, "utf8");
  console.log(`[OK] wrote ${path.relative(projectRoot, path.join(pageDir, "index.html"))}`);
  if (!fs.existsSync(path.join(pageDir, "og.png"))) {
    console.warn(`[WARN] ${path.relative(projectRoot, path.join(pageDir, "og.png"))} missing; run generate_message.mjs first`);
  }
}

const rootHtml = renderPage(template, editions[0], latestId, SITE_URL);
fs.writeFileSync(indexPath, rootHtml, "utf8");
console.log(`[OK] wrote index.html (latest = ${latestId})`);
