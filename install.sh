#!/usr/bin/env bash
# Installs the better-coding / better-coding-review / domain-modelling Claude Code skills and the
# Reviewer and Auditor subagents, and optionally the
# cross-tool project files (AGENTS.md, Devin, Kiro) for the repo you're standing in.
#
# With no flags: downloads this repo and installs both skills into your user-level Claude Code
# skills folder (~/.claude/skills/). That's a one-time, per-machine install, both skills are then
# available in every project you open from now on, no per-project setup.
#
# --project: additionally copies AGENTS.md, a Devin plugin manifest, and a Kiro steering file into
# the CURRENT directory. Those are per-project files, not per-machine, because Devin and Kiro read
# project-local instructions instead of a user-global skill folder the way Claude Code does. Run
# this from inside whichever repo you want them in, and commit the results if you want your team to
# get them too.
#
# --skip-claude: skip the Claude Code install, useful if you only want the project files this run.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh -o install.sh
#   bash install.sh --project --skip-claude

set -euo pipefail

REPO_OWNER="Kritantasasanroy"
REPO_NAME="better-coding-skill"
BRANCH="main"
TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${BRANCH}.tar.gz"
SKILLS_DIR="${HOME}/.claude/skills"

PROJECT=false
SKIP_CLAUDE=false

for arg in "$@"; do
  case "$arg" in
    --project) PROJECT=true ;;
    --skip-claude) SKIP_CLAUDE=true ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: install.sh [--project] [--skip-claude]" >&2
      exit 1
      ;;
  esac
done

echo "better-coding installer"
echo "Downloading ${REPO_OWNER}/${REPO_NAME}@${BRANCH} ..."

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

if ! curl -fsSL "$TARBALL_URL" -o "$TMP_DIR/repo.tar.gz"; then
  echo "Could not download $TARBALL_URL. Check your connection, or install manually:" >&2
  echo "  git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git" >&2
  exit 1
fi

tar -xzf "$TMP_DIR/repo.tar.gz" -C "$TMP_DIR"
EXTRACTED_ROOT="$TMP_DIR/${REPO_NAME}-${BRANCH}"

if [ ! -d "$EXTRACTED_ROOT" ]; then
  echo "Unexpected archive layout under $TMP_DIR. Install manually instead:" >&2
  echo "  git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git" >&2
  exit 1
fi

if [ "$SKIP_CLAUDE" = false ]; then
  echo ""
  echo "Installing Claude Code skills to $SKILLS_DIR ..."
  mkdir -p "$SKILLS_DIR"

  for skill in better-coding better-coding-review domain-modelling; do
    dest="$SKILLS_DIR/$skill"
    rm -rf "$dest"
    cp -R "$EXTRACTED_ROOT/$skill" "$dest"
    echo "  - $skill -> $dest"
  done

  AGENTS_DIR="${HOME}/.claude/agents"
  mkdir -p "$AGENTS_DIR"
  for agent in better-coding-reviewer better-coding-auditor; do
    cp "$EXTRACTED_ROOT/agents/$agent.md" "$AGENTS_DIR/$agent.md"
    echo "  - agent $agent -> $AGENTS_DIR/$agent.md"
  done

  echo ""
  echo "Done. All three skills, plus the Reviewer and Auditor agents, are available in every project on this machine now."
  echo "Try: /better-coding-review lite   (from inside any repo, in Claude Code)"
fi

if [ "$PROJECT" = true ]; then
  PROJECT_DIR="$(pwd)"
  echo ""
  echo "Installing cross-tool project files into $PROJECT_DIR ..."

  cp "$EXTRACTED_ROOT/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
  echo "  - AGENTS.md (read automatically by Devin, Kiro, Qoder, OpenCode, and other AGENTS.md-aware tools)"

  mkdir -p "$PROJECT_DIR/.devin-plugin"
  cp "$EXTRACTED_ROOT/.devin-plugin/plugin.json" "$PROJECT_DIR/.devin-plugin/plugin.json"
  echo "  - .devin-plugin/plugin.json"

  mkdir -p "$PROJECT_DIR/.kiro/steering"
  cp "$EXTRACTED_ROOT/.kiro/steering/better-coding.md" "$PROJECT_DIR/.kiro/steering/better-coding.md"
  echo "  - .kiro/steering/better-coding.md"

  mkdir -p "$PROJECT_DIR/.cursor/rules"
  cp "$EXTRACTED_ROOT/.cursor/rules/better-coding.mdc" "$PROJECT_DIR/.cursor/rules/better-coding.mdc"
  echo "  - .cursor/rules/better-coding.mdc"

  mkdir -p "$PROJECT_DIR/.windsurf/rules"
  cp "$EXTRACTED_ROOT/.windsurf/rules/better-coding.md" "$PROJECT_DIR/.windsurf/rules/better-coding.md"
  echo "  - .windsurf/rules/better-coding.md"

  mkdir -p "$PROJECT_DIR/.clinerules"
  cp "$EXTRACTED_ROOT/.clinerules/better-coding.md" "$PROJECT_DIR/.clinerules/better-coding.md"
  echo "  - .clinerules/better-coding.md"

  echo ""
  echo "Commit these into the repo if you want your team to get them too."
elif [ "$SKIP_CLAUDE" = false ]; then
  echo ""
  echo "This installed Claude Code only. AGENTS.md/Devin/Kiro files are per-project, not"
  echo "per-machine: cd into a specific repo and re-run with --project to add them there."
fi
