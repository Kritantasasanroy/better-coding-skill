<#
.SYNOPSIS
  Installs the better-coding / better-coding-review Claude Code skills, and optionally the
  cross-tool project files (AGENTS.md, Devin, Kiro) for the repo you're standing in.

.DESCRIPTION
  With no flags: downloads this repo and installs both skills into your user-level Claude Code
  skills folder (~/.claude/skills/). That's a one-time, per-machine install, both skills are then
  available in every project you open from now on, no per-project setup.

  -Project: additionally copies AGENTS.md, a Devin plugin manifest, and a Kiro steering file into
  the CURRENT directory. Those are per-project files, not per-machine, because Devin and Kiro read
  project-local instructions instead of a user-global skill folder the way Claude Code does. Run
  this from inside whichever repo you want them in, and commit the results if you want your team to
  get them too.

  -SkipClaude: skip the Claude Code install, useful if you only want the project files this run.

.EXAMPLE
  irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 | iex

.EXAMPLE
  # from inside a specific project repo, after the one-time install above
  irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 -OutFile install.ps1
  .\install.ps1 -Project -SkipClaude
#>

[CmdletBinding()]
param(
    [switch]$Project,
    [switch]$SkipClaude
)

$ErrorActionPreference = 'Stop'

$RepoOwner = 'Kritantasasanroy'
$RepoName  = 'better-coding-skill'
$Branch    = 'main'
$ZipUrl    = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/$Branch.zip"
$SkillsDir = Join-Path $HOME '.claude\skills'

Write-Host 'better-coding installer' -ForegroundColor Cyan
Write-Host "Downloading $RepoOwner/$RepoName@$Branch ..."

$tempZip = Join-Path $env:TEMP "better-coding-skill-$([guid]::NewGuid()).zip"
$tempDir = Join-Path $env:TEMP "better-coding-skill-$([guid]::NewGuid())"

try {
    Invoke-WebRequest -Uri $ZipUrl -OutFile $tempZip -UseBasicParsing
} catch {
    Write-Error "Could not download $ZipUrl. Check your connection, or install manually: git clone https://github.com/$RepoOwner/$RepoName.git"
    exit 1
}

Expand-Archive -Path $tempZip -DestinationPath $tempDir -Force
$extractedRoot = Join-Path $tempDir "$RepoName-$Branch"

if (-not (Test-Path $extractedRoot)) {
    Write-Error "Unexpected archive layout under $tempDir. Install manually instead: git clone https://github.com/$RepoOwner/$RepoName.git"
    exit 1
}

if (-not $SkipClaude) {
    Write-Host "`nInstalling Claude Code skills to $SkillsDir ..."
    New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null

    foreach ($skill in @('better-coding', 'better-coding-review', 'domain-modelling')) {
        $source = Join-Path $extractedRoot $skill
        $dest   = Join-Path $SkillsDir $skill
        if (Test-Path $dest) {
            Remove-Item -Recurse -Force $dest
        }
        Copy-Item -Recurse -Path $source -Destination $dest
        Write-Host "  - $skill -> $dest" -ForegroundColor Green
    }

    $AgentsDir = Join-Path $HOME '.claude\agents'
    New-Item -ItemType Directory -Force -Path $AgentsDir | Out-Null
    foreach ($agent in @('better-coding-reviewer', 'better-coding-auditor')) {
        $source = Join-Path $extractedRoot "agents\$agent.md"
        $dest   = Join-Path $AgentsDir "$agent.md"
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "  - agent $agent -> $dest" -ForegroundColor Green
    }

    Write-Host "`nDone. All three skills, plus the Reviewer and Auditor agents, are available in every project on this machine now."
    Write-Host 'Try: /better-coding-review lite   (from inside any repo, in Claude Code)'
}

if ($Project) {
    $projectDir = (Get-Location).Path
    Write-Host "`nInstalling cross-tool project files into $projectDir ..."

    Copy-Item -Path (Join-Path $extractedRoot 'AGENTS.md') -Destination (Join-Path $projectDir 'AGENTS.md') -Force
    Write-Host '  - AGENTS.md (read automatically by Devin, Kiro, Qoder, OpenCode, and other AGENTS.md-aware tools)' -ForegroundColor Green

    $devinDir = Join-Path $projectDir '.devin-plugin'
    New-Item -ItemType Directory -Force -Path $devinDir | Out-Null
    Copy-Item -Path (Join-Path $extractedRoot '.devin-plugin\plugin.json') -Destination (Join-Path $devinDir 'plugin.json') -Force
    Write-Host '  - .devin-plugin\plugin.json' -ForegroundColor Green

    $kiroDir = Join-Path $projectDir '.kiro\steering'
    New-Item -ItemType Directory -Force -Path $kiroDir | Out-Null
    Copy-Item -Path (Join-Path $extractedRoot '.kiro\steering\better-coding.md') -Destination (Join-Path $kiroDir 'better-coding.md') -Force
    Write-Host '  - .kiro\steering\better-coding.md' -ForegroundColor Green

    $cursorDir = Join-Path $projectDir '.cursor\rules'
    New-Item -ItemType Directory -Force -Path $cursorDir | Out-Null
    Copy-Item -Path (Join-Path $extractedRoot '.cursor\rules\better-coding.mdc') -Destination (Join-Path $cursorDir 'better-coding.mdc') -Force
    Write-Host '  - .cursor\rules\better-coding.mdc' -ForegroundColor Green

    $windsurfDir = Join-Path $projectDir '.windsurf\rules'
    New-Item -ItemType Directory -Force -Path $windsurfDir | Out-Null
    Copy-Item -Path (Join-Path $extractedRoot '.windsurf\rules\better-coding.md') -Destination (Join-Path $windsurfDir 'better-coding.md') -Force
    Write-Host '  - .windsurf\rules\better-coding.md' -ForegroundColor Green

    $clineDir = Join-Path $projectDir '.clinerules'
    New-Item -ItemType Directory -Force -Path $clineDir | Out-Null
    Copy-Item -Path (Join-Path $extractedRoot '.clinerules\better-coding.md') -Destination (Join-Path $clineDir 'better-coding.md') -Force
    Write-Host '  - .clinerules\better-coding.md' -ForegroundColor Green

    Write-Host "`nCommit these into the repo if you want your team to get them too." -ForegroundColor Cyan
} elseif (-not $SkipClaude) {
    Write-Host "`nThis installed Claude Code only. AGENTS.md/Devin/Kiro files are per-project, not" -ForegroundColor Yellow
    Write-Host 'per-machine: cd into a specific repo and re-run with -Project to add them there.' -ForegroundColor Yellow
}

Remove-Item -Recurse -Force $tempZip, $tempDir -ErrorAction SilentlyContinue
