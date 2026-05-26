#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/";

function parseArgs(argv) {
  const out = { jsonPath: null, projectRoot: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--project-root") {
      out.projectRoot = argv[i + 1];
      i += 1;
    } else if (!out.jsonPath) {
      out.jsonPath = argv[i];
    }
  }
  if (!out.jsonPath) throw new Error("Usage: node generate_message.mjs data/YYYY-MM-DD.json [--project-root <root>]");
  return out;
}

function isProjectRoot(dir) {
  return fs.existsSync(path.join(dir, "index.html")) && fs.existsSync(path.join(dir, "data"));
}

function findProjectRoot(jsonPath, explicit) {
  const starts = [explicit, process.env.DAILYTECHBRIEF_ROOT, jsonPath, process.cwd()].filter(Boolean);
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

function escText(value) {
  return String(value ?? "");
}

function buildText(edition) {
  const lines = [
    "📌 KAIST 경영대학 테크 네트워크",
    "데일리 테크 브리프",
    `${edition.id.replaceAll("-", ".")} ${edition.dayOfWeek}요일`,
    "",
    `전체 보기 👉 ${SITE_URL}date/${edition.id}/`,
    "",
    "🔎 오늘의 키워드",
    edition.newsItems.flatMap((item) => item.keywords ?? []).join(" · "),
    "",
  ];

  for (const item of edition.newsItems) {
    lines.push(`${String(item.order).padStart(2, "0")}. ${item.title}`);
    lines.push(item.summary);
    lines.push("");
  }

  lines.push(`전체 보기 👉 ${SITE_URL}date/${edition.id}/`);
  lines.push("KAIST 경영대학 테크 네트워크");
  return lines.join(os.EOL);
}

function psString(value) {
  return `'${String(value).replaceAll("'", "''")}'`;
}

function renderWithPowerShell(edition, projectRoot, cardPath, ogPath) {
  if (process.platform !== "win32") {
    throw new Error("PNG fallback renderer requires Windows PowerShell. Use the Python Playwright script on non-Windows hosts.");
  }

  const headlines = edition.newsItems.map((item) => item.title);
  const keywords = edition.newsItems.flatMap((item) => item.keywords ?? []);
  const script = `
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$projectRoot = ${psString(projectRoot)}
$cardPath = ${psString(cardPath)}
$ogPath = ${psString(ogPath)}
$dateLine = ${psString(`${edition.id.replaceAll("-", ".")} ${edition.dayOfWeek}요일`)}
$headlines = @(${headlines.map(psString).join(",")})
$keywords = @(${keywords.map(psString).join(",")})
$logoPath = Join-Path $projectRoot 'KCB_Logo.png'

function New-Font([string]$Family, [float]$Size, [string]$Style = 'Bold') {
  New-Object System.Drawing.Font($Family, $Size, [System.Drawing.FontStyle]::$Style, [System.Drawing.GraphicsUnit]::Pixel)
}

function Draw-Edition([int]$Width, [int]$Height, [string]$OutPath, [bool]$Og) {
  $bmp = New-Object System.Drawing.Bitmap $Width, $Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $bg = [System.Drawing.Color]::FromArgb(31,72,153)
  $deep = [System.Drawing.Color]::FromArgb(21,50,107)
  $g.Clear($bg)
  $logo = [System.Drawing.Image]::FromFile($logoPath)
  $white = [System.Drawing.Brushes]::White
  $muted = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(210,225,255))
  $deepBrush = New-Object System.Drawing.SolidBrush $deep

  if ($Og) {
    $g.FillRectangle($deepBrush, 40, 260, 1120, 260)
    $g.DrawImage($logo, 56, 44, 250, 74)
    $g.DrawString('KAIST Business Tech Network', (New-Font 'Segoe UI' 34), $white, 330, 58)
    $g.DrawString('Daily Tech Brief', (New-Font 'Segoe UI' 68), $white, 56, 140)
    $g.DrawString($dateLine, (New-Font 'Malgun Gothic' 42), $white, 760, 150)
    $g.DrawString('Keywords', (New-Font 'Segoe UI' 20), $white, 72, 286)
    $font = New-Font 'Malgun Gothic' 28
    $x = 72; $y = 336
    foreach ($kw in $keywords[0..([Math]::Min($keywords.Length - 1, 9))]) {
      $size = $g.MeasureString($kw, $font)
      if ($x + $size.Width -gt 1080) { $x = 72; $y += 48 }
      $g.DrawString($kw, $font, $white, $x, $y)
      $x += [int]$size.Width + 24
    }
  } else {
    $g.FillEllipse((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(35,255,255,255))), 700, -120, 520, 520)
    $g.FillRectangle($deepBrush, 70, 360, 940, 250)
    $g.DrawImage($logo, 70, 70, 270, 86)
    $g.DrawString('KAIST Business Tech Network', (New-Font 'Segoe UI' 34), $white, 370, 88)
    $g.DrawString('Daily Tech Brief', (New-Font 'Segoe UI' 64), $white, 70, 190)
    $g.DrawString($dateLine, (New-Font 'Malgun Gothic' 52), $white, 70, 270)
    $kwFont = New-Font 'Malgun Gothic' 24
    $x = 100; $y = 398
    foreach ($kw in $keywords) {
      $size = $g.MeasureString($kw, $kwFont)
      if ($x + $size.Width -gt 950) { $x = 100; $y += 36 }
      if ($y -lt 590) { $g.DrawString($kw, $kwFont, $white, $x, $y) }
      $x += [int]$size.Width + 18
    }
    $numFont = New-Font 'Consolas' 26
    $headFont = New-Font 'Malgun Gothic' 28
    $y = 655
    for ($i = 0; $i -lt $headlines.Length; $i++) {
      $g.DrawString(('{0:D2}' -f ($i + 1)), $numFont, $muted, 80, $y + 4)
      $g.DrawString($headlines[$i], $headFont, $white, 150, $y)
      $y += 92
    }
    $g.FillRectangle([System.Drawing.Brushes]::White, 760, 1780, 250, 70)
    $g.DrawString('View All ->', (New-Font 'Segoe UI' 28), (New-Object System.Drawing.SolidBrush $bg), 808, 1798)
  }

  $bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $logo.Dispose(); $deepBrush.Dispose(); $muted.Dispose(); $g.Dispose(); $bmp.Dispose()
}

Draw-Edition 1080 1920 $cardPath $false
Draw-Edition 1200 630 $ogPath $true
`;

  const result = spawnSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], {
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || "PowerShell renderer failed.");
  }
}

const args = parseArgs(process.argv.slice(2));
const projectRoot = findProjectRoot(args.jsonPath, args.projectRoot);
const jsonPath = path.isAbsolute(args.jsonPath) ? args.jsonPath : path.resolve(process.cwd(), args.jsonPath);
const edition = JSON.parse(fs.readFileSync(jsonPath, "utf8"));

const messageDir = path.join(projectRoot, "Message", edition.id);
const dateDir = path.join(projectRoot, "date", edition.id);
fs.mkdirSync(messageDir, { recursive: true });
fs.mkdirSync(dateDir, { recursive: true });

const textPath = path.join(messageDir, "text.txt");
const cardPath = path.join(messageDir, "card.png");
const ogPath = path.join(dateDir, "og.png");

fs.writeFileSync(textPath, buildText(edition), "utf8");
console.log(`[OK] wrote ${path.relative(projectRoot, textPath)}`);
renderWithPowerShell(edition, projectRoot, cardPath, ogPath);
console.log(`[OK] wrote ${path.relative(projectRoot, cardPath)}`);
console.log(`[OK] wrote ${path.relative(projectRoot, ogPath)}`);
