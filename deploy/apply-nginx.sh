#!/usr/bin/env bash
# 把本目录 Nginx 配置同步到服务器并 reload。
# 用法（仓库根目录）：./deploy/apply-nginx.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${DEPLOY_ROOT:-/opt/alchemy}"
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=10)
SCP=(scp -o BatchMode=yes -o ConnectTimeout=10)

info() { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
ok()   { printf '\033[0;32m[OK]\033[0m    %s\n' "$*"; }
err()  { printf '\033[0;31m[ERR]\033[0m   %s\n' "$*" >&2; }

if [[ -z "${DEPLOY_HOST:-}" ]]; then
  err "DEPLOY_HOST 未设置，例如: export DEPLOY_HOST=root@your-server"
  exit 1
fi
HOST="$DEPLOY_HOST"

"${SSH[@]}" "$HOST" "test -d $REMOTE" || {
  err "服务器 $REMOTE 不存在"
  exit 1
}

info "同步 Nginx 片段与站点配置"
"${SSH[@]}" "$HOST" "mkdir -p $REMOTE/conf/nginx $REMOTE/conf/tls"
"${SCP[@]}" \
  "$ROOT/deploy/nginx-locations.conf" \
  "$HOST:$REMOTE/conf/nginx/locations.conf"
"${SCP[@]}" \
  "$ROOT/deploy/nginx-cloudflare-realip.conf" \
  "$HOST:/etc/nginx/conf.d/cloudflare-realip.conf"
"${SCP[@]}" \
  "$ROOT/deploy/nginx-alchemy.conf" \
  "$HOST:/etc/nginx/conf.d/alchemy.conf"
"${SCP[@]}" \
  "$ROOT/deploy/nginx-alchemy-ssl.conf" \
  "$HOST:/etc/nginx/conf.d/alchemy-ssl.conf"

info "同步源站证书配置"
"${SCP[@]}" \
  "$ROOT/deploy/origin-openssl.cnf" \
  "$HOST:$REMOTE/conf/tls/origin-openssl.cnf"

info "若无源站证书则生成自签（CA:FALSE + SAN；之后可换成 Cloudflare Origin CA）"
"${SSH[@]}" "$HOST" "set -e
  CRT=$REMOTE/conf/tls/origin.crt
  KEY=$REMOTE/conf/tls/origin.key
  CFG=$REMOTE/conf/tls/origin-openssl.cnf
  if [[ ! -s \"\$CRT\" || ! -s \"\$KEY\" ]]; then
    openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
      -keyout \"\$KEY\" -out \"\$CRT\" \
      -config \"\$CFG\"
    chmod 600 \"\$KEY\"
  fi
"

info "nginx -t && reload"
"${SSH[@]}" "$HOST" "rm -f /etc/nginx/sites-enabled/default; nginx -t && nginx -s reload"

ok "Nginx 已更新"
