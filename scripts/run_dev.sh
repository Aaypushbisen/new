#!/usr/bin/env bash
set -euo pipefail

export ALLOWED_ORIGINS="*"
export API_KEY="dev"
export PYTHONUNBUFFERED=1

python3 -m app.app

