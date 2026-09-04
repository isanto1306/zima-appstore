#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
ACTION_REPO="${ACTION_REPO:-IceWhaleTech/build-appstore-action}"
ACTION_REF="${ACTION_REF:-v1}"
ACTION_RAW_BASE="${ACTION_RAW_BASE:-https://raw.githubusercontent.com/$ACTION_REPO/$ACTION_REF}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

SOURCE_DIR="${SOURCE_DIR:-$ROOT_DIR}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/dist}"
CACHE_DIR="${CACHE_DIR:-$ROOT_DIR/.cache/build_appstore}"
IMAGE_SIZE_CACHE_FILE="${IMAGE_SIZE_CACHE_FILE:-$CACHE_DIR/image-size-cache.json}"
IMAGE_DIGEST_CACHE_FILE="${IMAGE_DIGEST_CACHE_FILE:-$CACHE_DIR/image-digest-cache.json}"
BASE_URL="${BASE_URL:-https://isanto1306.github.io/zima-appstore}"
REMOTE_BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/build-appstore-action.XXXXXX")"

cleanup() {
  rm -rf "$REMOTE_BUILD_DIR"
}
trap cleanup EXIT

mkdir -p "$CACHE_DIR"

curl -fsSL "$ACTION_RAW_BASE/scripts/build_appstore.py" \
  -o "$REMOTE_BUILD_DIR/build_appstore.py"
curl -fsSL "$ACTION_RAW_BASE/requirements.txt" \
  -o "$REMOTE_BUILD_DIR/requirements.txt"

python3 -m pip install -r "$REMOTE_BUILD_DIR/requirements.txt"

python3 "$REMOTE_BUILD_DIR/build_appstore.py" \
  --source "$SOURCE_DIR" \
  --output "$OUTPUT_DIR" \
  --base-url "$BASE_URL" \
  --cache-file "$IMAGE_SIZE_CACHE_FILE" \
  --digest-cache-file "$IMAGE_DIGEST_CACHE_FILE"
