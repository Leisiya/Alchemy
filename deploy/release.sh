#!/usr/bin/env bash
# 日常一键发布：本机打包 → rsync 到服务器 → 重启后端
# 首次上线（装 JDK / Nginx / Miniconda）不用这个脚本。
#
# 用法（在仓库根目录）:
#   ./deploy/release.sh              # 后端 + 前端 + 筛股源码，然后重启
#   ./deploy/release.sh backend      # 只发 jar 并重启
#   ./deploy/release.sh frontend     # 只发 dist（Nginx 静态，无需重启 Java）
#   ./deploy/release.sh python       # 只发筛股源码（不覆盖服务器 .venv）
#   SKIP_BUILD=1 ./deploy/release.sh # 不重新编译，只同步已有产物并重启
#   ./deploy/release.sh --deps       # 同步 Python 后在服务器 pip 安装依赖
#
# 环境变量:
#   DEPLOY_HOST   必填，例如 root@your-server
#   DEPLOY_ROOT   默认 /opt/alchemy

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${DEPLOY_ROOT:-/opt/alchemy}"
SKIP_BUILD="${SKIP_BUILD:-0}"
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=10)
RSYNC=(rsync -az --delete)
TARGET="all"
INSTALL_DEPS=0

info()  { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[0;32m[OK]\033[0m    %s\n' "$*"; }
err()   { printf '\033[0;31m[ERR]\033[0m   %s\n' "$*" >&2; }

if [[ -z "${DEPLOY_HOST:-}" ]]; then
  err "DEPLOY_HOST 未设置，例如: export DEPLOY_HOST=root@your-server"
  exit 1
fi
HOST="$DEPLOY_HOST"

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
    --deps) INSTALL_DEPS=1 ;;
    all|backend|frontend|python) TARGET="$arg" ;;
    *) err "未知参数: $arg"; usage; exit 1 ;;
  esac
done

need_backend=0
need_frontend=0
need_python=0
need_restart=0
case "$TARGET" in
  all) need_backend=1; need_frontend=1; need_python=1; need_restart=1 ;;
  backend) need_backend=1; need_restart=1 ;;
  frontend) need_frontend=1 ;;
  python) need_python=1 ;;
esac

"${SSH[@]}" "$HOST" "test -d $REMOTE/app" || {
  err "服务器 $REMOTE 不像已完成首次部署，请先按 deploy/README.md 做完首次上线"
  exit 1
}

if [[ "$need_backend" -eq 1 && "$SKIP_BUILD" != "1" ]]; then
  info "打包后端"
  (cd "$ROOT" && mvn -DskipTests package)
fi

if [[ "$need_frontend" -eq 1 && "$SKIP_BUILD" != "1" ]]; then
  info "打包前端"
  (cd "$ROOT/ruoyi-ui" && npm run build:prod)
fi

if [[ "$need_backend" -eq 1 ]]; then
  local_jar="$ROOT/ruoyi-admin/target/ruoyi-admin.jar"
  [[ -f "$local_jar" ]] || { err "找不到 $local_jar"; exit 1; }
  info "同步 jar → $REMOTE/app/"
  "${RSYNC[@]}" -e "ssh -o BatchMode=yes" "$local_jar" "$HOST:$REMOTE/app/ruoyi-admin.jar"
fi

if [[ "$need_frontend" -eq 1 ]]; then
  [[ -f "$ROOT/ruoyi-ui/dist/index.html" ]] || { err "找不到 ruoyi-ui/dist/index.html"; exit 1; }
  info "同步前端 → $REMOTE/ui/"
  "${RSYNC[@]}" -e "ssh -o BatchMode=yes" "$ROOT/ruoyi-ui/dist/" "$HOST:$REMOTE/ui/"
fi

if [[ "$need_python" -eq 1 ]]; then
  info "同步筛股源码 → $REMOTE/stock-screening-service/（不含 .venv）"
  "${RSYNC[@]}" -e "ssh -o BatchMode=yes" \
    --exclude '.venv' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' --exclude '.DS_Store' \
    "$ROOT/stock-screening-service/" "$HOST:$REMOTE/stock-screening-service/"
fi

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
  info "服务器安装 Python 依赖"
  "${SSH[@]}" "$HOST" "set -e
    PY=$REMOTE/stock-screening-service/.venv/bin/python
    test -x \"\$PY\" || { echo '服务器缺少 .venv，请先完成首次部署'; exit 1; }
    \"\$PY\" -m pip install -U pip -i $PIP_MIRROR
    \"\$PY\" -m pip install 'numpy==1.26.4' -i $PIP_MIRROR
    \"\$PY\" -m pip install -r $REMOTE/stock-screening-service/requirements.txt -i $PIP_MIRROR
  "
fi

if [[ "$need_restart" -eq 1 ]]; then
  info "重启后端 alchemy"
  "${SSH[@]}" "$HOST" "systemctl restart alchemy"
  info "等待启动"
  ok_boot=0
  for _ in $(seq 1 40); do
    code="$("${SSH[@]}" "$HOST" "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/" || true)"
    if [[ "$code" == "200" ]]; then
      ok_boot=1
      break
    fi
    sleep 2
  done
  if [[ "$ok_boot" -ne 1 ]]; then
    err "后端未在预期时间内返回 200，查看: ssh $HOST journalctl -u alchemy -n 80 --no-pager"
    exit 1
  fi
  ok "后端已起来 (HTTP 200)"
else
  ok "静态/源码已同步，无需重启 Java"
fi

ok "发布完成"
