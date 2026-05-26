param(
  [string]$SkillName = "tech-news-daily",
  [string]$DestinationRoot = (Join-Path $HOME ".codex\skills"),
  [switch]$BackupExisting,
  [switch]$InstallPlaywright
)

$ErrorActionPreference = "Stop"

function Resolve-ExistingPath($Path, $Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "$Label not found: $Path"
  }
  return (Resolve-Path -LiteralPath $Path).Path
}

$repoRoot = $PSScriptRoot
$source = Join-Path $repoRoot ".codex\skills\$SkillName"
$source = Resolve-ExistingPath $source "Skill source"

$skillMd = Join-Path $source "SKILL.md"
if (-not (Test-Path -LiteralPath $skillMd)) {
  throw "SKILL.md not found in $source"
}

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null
$destinationRootResolved = (Resolve-Path -LiteralPath $DestinationRoot).Path
$destination = Join-Path $destinationRootResolved $SkillName

if (Test-Path -LiteralPath $destination) {
  $destinationResolved = (Resolve-Path -LiteralPath $destination).Path
  if (-not $destinationResolved.StartsWith($destinationRootResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to update destination outside Codex skills root: $destinationResolved"
  }

  if ($BackupExisting) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = "$destination.bak-$timestamp"
    Move-Item -LiteralPath $destinationResolved -Destination $backup
    Write-Output "[OK] Backed up existing skill to $backup"
  } else {
    Remove-Item -LiteralPath $destinationResolved -Recurse -Force
  }
}

Copy-Item -LiteralPath $source -Destination $destination -Recurse
Write-Output "[OK] Installed $SkillName to $destination"

$validator = Join-Path $HOME ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
if (Test-Path -LiteralPath $validator) {
  $env:PYTHONUTF8 = "1"
  python $validator $destination
} else {
  Write-Output "[WARN] Codex skill validator not found; skipped validation"
}

if ($InstallPlaywright) {
  python -m playwright install chromium
}

Write-Output "[OK] Restart or refresh Codex if the skill list has not updated."

