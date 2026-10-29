#!/usr/bin/env bash
set -Eeuo pipefail

# Download the latest successful Timison Browser Next workflow artifact,
# verify its package and pinned signer, then offer a non-destructive install.
REPO='ihearta380/Fulguris'
BRANCH='timison-browser-next-development'
WORKFLOW='Timison Browser Next'
EXPECTED_ARTIFACT='timison-browser-next-debug-apk'
PROJECT_DIR="${TIMISON_BROWSER_NEXT_DIR:-$HOME/Developer/timison-browser-next}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
PYTHON="${TIMISON_PYTHON:-python3}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$ANDROID_HOME}"

command -v gh >/dev/null || { echo 'ERROR: install GitHub CLI (brew install gh)' >&2; exit 1; }
command -v "$PYTHON" >/dev/null || { echo 'ERROR: python3 missing' >&2; exit 1; }
gh auth status >/dev/null || { echo 'ERROR: gh auth login required' >&2; exit 1; }
[[ -n "${TIMISON_SIGNING_CERT_SHA256:-}" ]] || {
  echo 'ERROR: set TIMISON_SIGNING_CERT_SHA256 to the pinned Timison certificate fingerprint.' >&2
  exit 1
}
[[ -f "$PROJECT_DIR/scripts/tools/install_timison_apk.py" ]] || {
  echo "ERROR: Timison Browser Next repo not found at $PROJECT_DIR" >&2
  exit 1
}

RUN_JSON="$(gh run list -R "$REPO" -b "$BRANCH" -L 50 --json databaseId,status,conclusion,headSha,workflowName,createdAt)"
RUN_ID="$(printf '%s' "$RUN_JSON" | "$PYTHON" -c 'import json,sys; runs=json.load(sys.stdin); matches=[r for r in runs if r.get("workflowName")=="Timison Browser Next"]; newest=max(matches,key=lambda r:r.get("createdAt", "")) if matches else None; print(newest["databaseId"] if newest and newest.get("status")=="completed" and newest.get("conclusion")=="success" else "")')"
if [[ -z "$RUN_ID" ]]; then
  echo 'ERROR: newest Timison workflow is not successful or was not found; refusing to install a stale artifact.' >&2
  exit 1
fi

ARTIFACTS="$(gh api "repos/$REPO/actions/runs/$RUN_ID/artifacts" --jq '.artifacts[] | select(.expired == false) | .name')"
if ! grep -Fxq "$EXPECTED_ARTIFACT" <<< "$ARTIFACTS"; then
  echo "ERROR: expected artifact '$EXPECTED_ARTIFACT' not present on run $RUN_ID" >&2
  exit 1
fi

SCRATCH="$PROJECT_DIR/.temp"
mkdir -p "$SCRATCH"
chmod 700 "$SCRATCH"
WORKDIR="$(mktemp -d "$SCRATCH/timison-deploy.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
printf 'Downloading %s from successful run %s\n' "$EXPECTED_ARTIFACT" "$RUN_ID"
gh run download "$RUN_ID" -R "$REPO" -n "$EXPECTED_ARTIFACT" -D "$WORKDIR"
APK_COUNT="$(find "$WORKDIR" -type f -name '*.apk' | wc -l | tr -d ' ')"
[[ "$APK_COUNT" == 1 ]] || { echo "ERROR: expected one APK, found $APK_COUNT" >&2; exit 1; }
APK="$(find "$WORKDIR" -type f -name '*.apk' -print -quit)"

# The project installer refuses unsigned/unexpected certificates and never
# falls back to uninstall or data clearing on INSTALL_FAILED_UPDATE_INCOMPATIBLE.
"$PYTHON" "$PROJECT_DIR/scripts/tools/install_timison_apk.py" \
  --apk "$APK" --certificate-sha256 "$TIMISON_SIGNING_CERT_SHA256"
