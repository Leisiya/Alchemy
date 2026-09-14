#!/usr/bin/env bash
# Alchemy 本地联调一键脚本：停旧进程 → 重新编译后端 → 启动前后端
# 用法:
#   ./start-dev.sh          # 等同 restart（保证按当前代码重新拉起）
#   ./start-dev.sh start    # 同上
#   ./start-dev.sh stop     # 仅停止
#   ./start-dev.sh status   # 查看状态
#   ./start-dev.sh restart  # 同上 start
#
# 环境变量（可选）:
#   SKIP_BUILD=1            # 跳过 mvn package（仅重启进程，不重编译）
#   BACKEND_PORT=8080
#   FRONTEND_PORT=1024      # 默认 1024（本机 :80 会被 vue-cli/portfinder 因多网卡 EACCES 改掉）

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_DIR="$ROOT/.runtime"
LOG_DIR="$RUNTIME_DIR/logs"
PID_BACKEND="$RUNTIME_DIR/backend.pid"
PID_FRONTEND="$RUNTIME_DIR/frontend.pid"
PORT_FRONTEND_FILE="$RUNTIME_DIR/frontend.port"
JAR="$ROOT/ruoyi-admin/target/ruoyi-admin.jar"
BACKEND_PORT="${BACKEND_PORT:-8080}"
FRONTEND_PORT="${FRONTEND_PORT:-1024}"

mkdir -p "$LOG_DIR"

info()  { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[0;32m[OK]\033[0m    %s\n' "$*"; }
warn()  { printf '\033[0;33m[WARN]\033[0m  %s\n' "$*"; }
err()   { printf '\033[0;31m[ERR]\033[0m   %s\n' "$*" >&2; }

pids_on_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true
  else
    true
  fi
}

# 检测当前用户能否绑定该端口（macOS 上 <1024 通常需要 root）
can_bind_port() {
  local port="$1"
  python3 - "$port" <<'PY' 2>/dev/null
import socket, sys
port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(("0.0.0.0", port))
except OSError:
    sys.exit(1)
finally:
    s.close()
sys.exit(0)
PY
}

resolve_frontend_port() {
  # 用与 vue-cli 相同的 portfinder，提前得到真实会占用的端口
  if [[ -f "$ROOT/ruoyi-ui/node_modules/portfinder/lib/portfinder.js" ]] || [[ -d "$ROOT/ruoyi-ui/node_modules/portfinder" ]]; then
    local actual
    actual="$(
      cd "$ROOT/ruoyi-ui"
      node -e "const pf=require('portfinder'); pf.basePort=Number(process.argv[1]); pf.getPortPromise().then(p=>console.log(p)).catch(()=>process.exit(1))" \
        "$FRONTEND_PORT" 2>/dev/null || true
    )"
    if [[ -n "$actual" && "$actual" != "$FRONTEND_PORT" ]]; then
      warn "端口 $FRONTEND_PORT 不可用（vue-cli/portfinder 将改用 $actual）"
      FRONTEND_PORT="$actual"
    fi
  fi
  if ! can_bind_port "$FRONTEND_PORT"; then
    err "端口 $FRONTEND_PORT 无法绑定，请设置 FRONTEND_PORT 后重试"
    exit 1
  fi
}

saved_frontend_port() {
  if [[ -f "$PORT_FRONTEND_FILE" ]]; then
    cat "$PORT_FRONTEND_FILE"
  else
    echo "$FRONTEND_PORT"
  fi
}

# 真正守护化（双 fork + setsid），避免脚本/终端退出后进程被带走
daemonize() {
  # usage: daemonize <pidfile> <logfile> <workdir> <command...>
  local pidfile="$1"
  local logfile="$2"
  local workdir="$3"
  shift 3
  python3 - "$pidfile" "$logfile" "$workdir" "$@" <<'PY'
import os, sys, time

pidfile, logfile, workdir = sys.argv[1], sys.argv[2], sys.argv[3]
cmd = sys.argv[4:]

# 第一 fork
if os.fork() > 0:
    # 父进程稍等 pidfile
    for _ in range(50):
        if os.path.exists(pidfile) and os.path.getsize(pidfile) > 0:
            sys.exit(0)
        time.sleep(0.05)
    sys.exit(0)

os.setsid()
# 第二 fork
if os.fork() > 0:
    os._exit(0)

os.chdir(workdir)
os.umask(0)

# 重定向 stdio
with open(logfile, "a", buffering=1) as log, open(os.devnull, "r") as devnull:
    os.dup2(devnull.fileno(), 0)
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    # 写 pid（子进程自身；exec 后同 pid）
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))
    os.execvp(cmd[0], cmd)
PY
}

kill_tree() {
  local pid="$1"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  local children
  children="$(pgrep -P "$pid" 2>/dev/null || true)"
  local c
  for c in $children; do
    kill_tree "$c"
  done
  kill -TERM "$pid" 2>/dev/null || true
}

wait_pid_exit() {
  local pid="$1"
  local name="$2"
  local n=0
  while kill -0 "$pid" 2>/dev/null; do
    n=$((n + 1))
    if [[ $n -ge 30 ]]; then
      warn "$name (pid:$pid) 未退出，强制 kill -9"
      kill -9 "$pid" 2>/dev/null || true
      # 子进程也可能残留
      local children
      children="$(pgrep -P "$pid" 2>/dev/null || true)"
      local c
      for c in $children; do
        kill -9 "$c" 2>/dev/null || true
      done
      break
    fi
    sleep 1
  done
}

stop_by_pidfile() {
  local pidfile="$1"
  local name="$2"
  if [[ ! -f "$pidfile" ]]; then
    return 0
  fi
  local pid
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  rm -f "$pidfile"
  if [[ -z "$pid" ]]; then
    return 0
  fi
  if kill -0 "$pid" 2>/dev/null; then
    info "停止 $name (pid:$pid)..."
    kill_tree "$pid"
    wait_pid_exit "$pid" "$name"
    ok "$name 已停止"
  fi
}

stop_port() {
  local port="$1"
  local name="$2"
  local pids
  pids="$(pids_on_port "$port")"
  if [[ -z "$pids" ]]; then
    return 0
  fi
  info "释放端口 $port ($name): $pids"
  local pid
  for pid in $pids; do
    kill_tree "$pid"
    wait_pid_exit "$pid" "$name:$port"
  done
}

# 兜底：按命令行特征杀掉可能由 IDE / 手工启动的旧实例
stop_stragglers() {
  local pids
  pids="$(pgrep -f 'ruoyi-admin\.jar|com\.ruoyi\.RuoYiApplication' 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    info "清理残留后端进程: $pids"
    local pid
    for pid in $pids; do
      kill_tree "$pid"
      wait_pid_exit "$pid" "backend"
    done
  fi

  pids="$(pgrep -f 'vue-cli-service serve' 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    local pid cwd
    for pid in $pids; do
      cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1 || true)"
      if [[ "$cwd" == "$ROOT/ruoyi-ui"* ]] || [[ -z "$cwd" ]]; then
        info "清理残留前端进程: $pid"
        kill_tree "$pid"
        wait_pid_exit "$pid" "frontend"
      fi
    done
  fi
}

stop_all() {
  info "停止已有前后端..."
  local fe_port
  fe_port="$(saved_frontend_port)"
  stop_by_pidfile "$PID_FRONTEND" "frontend"
  stop_by_pidfile "$PID_BACKEND" "backend"
  stop_port "$fe_port" "frontend"
  # 兼容默认 80 / 回退 1024
  stop_port 80 "frontend"
  stop_port 1024 "frontend"
  stop_port "$BACKEND_PORT" "backend"
  stop_stragglers
  rm -f "$PORT_FRONTEND_FILE"
  ok "旧进程已清理"
}

build_backend() {
  if [[ "${SKIP_BUILD:-0}" == "1" ]]; then
    warn "SKIP_BUILD=1，跳过后端编译"
    if [[ ! -f "$JAR" ]]; then
      err "缺少 $JAR，无法跳过编译"
      exit 1
    fi
    return 0
  fi
  info "重新编译后端（确保加载最新代码）..."
  (
    cd "$ROOT"
    mvn -pl ruoyi-admin -am package -DskipTests -q
  )
  if [[ ! -f "$JAR" ]]; then
    err "编译完成但未找到 $JAR"
    exit 1
  fi
  ok "后端编译完成: $JAR"
}

start_backend() {
  info "启动后端 :$BACKEND_PORT ..."
  : >"$LOG_DIR/backend.log"
  # 本机若配置了 SOCKS 代理（如 127.0.0.1:7897），会劫持 JDBC；启动时显式清空
  daemonize "$PID_BACKEND" "$LOG_DIR/backend.log" "$ROOT" \
    java \
      -DsocksProxyHost= \
      -DsocksProxyPort= \
      -Djava.net.preferIPv4Stack=true \
      -Duser.timezone=Asia/Shanghai \
      -Xms512m -Xmx1024m \
      -jar "$JAR"
  ok "后端已启动 pid=$(cat "$PID_BACKEND")，日志: $LOG_DIR/backend.log"
}

start_frontend() {
  if [[ ! -d "$ROOT/ruoyi-ui/node_modules" ]]; then
    info "安装前端依赖..."
    (
      cd "$ROOT/ruoyi-ui"
      npm install --registry=https://registry.npmmirror.com
    )
  fi
  resolve_frontend_port
  echo "$FRONTEND_PORT" >"$PORT_FRONTEND_FILE"
  info "启动前端 :$FRONTEND_PORT ..."
  : >"$LOG_DIR/frontend.log"
  # vue.config.js 读取 process.env.port / npm_config_port
  daemonize "$PID_FRONTEND" "$LOG_DIR/frontend.log" "$ROOT/ruoyi-ui" \
    env port="$FRONTEND_PORT" npm run dev
  ok "前端已启动 pid=$(cat "$PID_FRONTEND")，日志: $LOG_DIR/frontend.log"
}

wait_ready() {
  local url="$1"
  local name="$2"
  local n=0
  info "等待 $name 就绪 ($url)..."
  while [[ $n -lt 90 ]]; do
    if curl -fsS -o /dev/null --connect-timeout 1 "$url" 2>/dev/null; then
      ok "$name 已就绪"
      return 0
    fi
    # 进程若已退出，尽早失败
    if [[ -f "$PID_BACKEND" ]] && [[ "$name" == "后端" ]]; then
      local pid
      pid="$(cat "$PID_BACKEND")"
      if ! kill -0 "$pid" 2>/dev/null; then
        err "后端进程已退出，请查看 $LOG_DIR/backend.log"
        return 1
      fi
    fi
    n=$((n + 1))
    sleep 1
  done
  err "$name 在 90s 内未响应，请查看日志: $LOG_DIR/"
  return 1
}

wait_frontend() {
  local n=0
  info "等待前端就绪 (http://127.0.0.1:${FRONTEND_PORT}/)..."
  while [[ $n -lt 120 ]]; do
    if [[ -n "$(pids_on_port "$FRONTEND_PORT")" ]]; then
      ok "前端端口 :$FRONTEND_PORT 已监听"
      return 0
    fi
    if [[ -f "$PID_FRONTEND" ]]; then
      local pid
      pid="$(cat "$PID_FRONTEND")"
      if ! kill -0 "$pid" 2>/dev/null; then
        err "前端进程已退出，请查看 $LOG_DIR/frontend.log"
        return 1
      fi
    fi
    n=$((n + 1))
    sleep 1
  done
  err "前端端口 :$FRONTEND_PORT 未监听，请查看 $LOG_DIR/frontend.log"
  return 1
}

status_one() {
  local pidfile="$1"
  local name="$2"
  local port="$3"
  if [[ -f "$pidfile" ]]; then
    local pid
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      printf '  %-10s running  pid=%-7s port=%s\n' "$name" "$pid" "$port"
      return 0
    fi
  fi
  local pids
  pids="$(pids_on_port "$port")"
  if [[ -n "$pids" ]]; then
    printf '  %-10s listening pid=%-7s port=%s (非本脚本 pidfile)\n' "$name" "$pids" "$port"
    return 0
  fi
  printf '  %-10s stopped\n' "$name"
}

show_status() {
  local fe_port
  fe_port="$(saved_frontend_port)"
  echo "Alchemy 本地服务状态:"
  status_one "$PID_BACKEND" "backend" "$BACKEND_PORT"
  status_one "$PID_FRONTEND" "frontend" "$fe_port"
  echo "日志目录: $LOG_DIR"
}

do_start() {
  stop_all
  build_backend
  start_backend
  start_frontend
  wait_ready "http://127.0.0.1:${BACKEND_PORT}/" "后端"
  wait_frontend
  echo
  ok "联调环境已就绪"
  echo "  前端: http://localhost:${FRONTEND_PORT}"
  echo "  后端: http://localhost:${BACKEND_PORT}"
  echo "  账号: admin / admin123"
  echo "  日志: $LOG_DIR/"
  echo "  停止: ./start-dev.sh stop"
}

cmd="${1:-restart}"
case "$cmd" in
  start|restart)
    do_start
    ;;
  stop)
    stop_all
    ;;
  status)
    show_status
    ;;
  *)
    err "未知命令: $cmd"
    echo "用法: ./start-dev.sh {start|stop|restart|status}"
    exit 1
    ;;
esac
