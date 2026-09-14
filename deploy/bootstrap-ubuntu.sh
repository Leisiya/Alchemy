#!/usr/bin/env bash
# Ubuntu 首次上线引导：目录、本机 MySQL/Redis、空库导表。
# 在仓库根目录：./deploy/bootstrap-ubuntu.sh
# 之后再用 ./deploy/release.sh 发应用，./deploy/apply-nginx.sh 配站点。
#
# 环境变量（必填）:
#   DEPLOY_HOST         例如 root@your-server
#   MYSQL_APP_PASSWORD  MySQL app 用户密码
#   REDIS_PASSWORD      Redis 密码
# 可选:
#   MYSQL_APP_USER      默认 appuser
#   DEPLOY_ROOT         默认 /opt/alchemy

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${DEPLOY_HOST:-}" ]]; then
  printf '\033[0;31m[ERR]\033[0m   DEPLOY_HOST 未设置，例如: export DEPLOY_HOST=root@your-server\n' >&2
  exit 1
fi
if [[ -z "${MYSQL_APP_PASSWORD:-}" ]]; then
  printf '\033[0;31m[ERR]\033[0m   MYSQL_APP_PASSWORD 未设置\n' >&2
  exit 1
fi
if [[ -z "${REDIS_PASSWORD:-}" ]]; then
  printf '\033[0;31m[ERR]\033[0m   REDIS_PASSWORD 未设置\n' >&2
  exit 1
fi
HOST="$DEPLOY_HOST"
REMOTE="${DEPLOY_ROOT:-/opt/alchemy}"
MYSQL_USER="${MYSQL_APP_USER:-appuser}"
MYSQL_PASS="$MYSQL_APP_PASSWORD"
REDIS_PASS="$REDIS_PASSWORD"
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=10)
SCP=(scp -o BatchMode=yes -o ConnectTimeout=10)

info() { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
ok()   { printf '\033[0;32m[OK]\033[0m    %s\n' "$*"; }
err()  { printf '\033[0;31m[ERR]\033[0m   %s\n' "$*" >&2; }

LOCAL_ENV="$ROOT/deploy/alchemy.env"
if [[ ! -f "$LOCAL_ENV" ]]; then
  err "找不到 $LOCAL_ENV"
  err "请先从 deploy/alchemy.env.example 复制并填入真实值: cp deploy/alchemy.env.example deploy/alchemy.env"
  exit 1
fi

info "建目录并拷 alchemy.env / systemd"
"${SSH[@]}" "$HOST" "mkdir -p $REMOTE/{app,ui,upload,logs,conf/nginx,conf/tls,stock-screening-service}"
"${SCP[@]}" "$LOCAL_ENV" "$HOST:$REMOTE/conf/alchemy.env"
"${SCP[@]}" "$ROOT/deploy/alchemy.service" "$HOST:/etc/systemd/system/alchemy.service"
"${SSH[@]}" "$HOST" "systemctl daemon-reload && systemctl enable alchemy"

info "MySQL：生产连 127.0.0.1；监听 0.0.0.0 供本机 start-dev.sh（防火墙再收紧来源 IP）"
"${SSH[@]}" "$HOST" "set -e
  mysql_cnf=/etc/mysql/mysql.conf.d/mysqld.cnf
  if grep -qE '^bind-address' \"\$mysql_cnf\"; then
    sed -i 's/^bind-address.*/bind-address\t\t= 0.0.0.0/' \"\$mysql_cnf\"
  else
    printf '\nbind-address = 0.0.0.0\n' >> \"\$mysql_cnf\"
  fi
  systemctl restart mysql
  mysql --protocol=socket <<SQL
CREATE DATABASE IF NOT EXISTS appdb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASS}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASS}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASS}';
ALTER USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASS}';
ALTER USER '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASS}';
ALTER USER '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASS}';
GRANT ALL PRIVILEGES ON appdb.* TO '${MYSQL_USER}'@'localhost';
GRANT ALL PRIVILEGES ON appdb.* TO '${MYSQL_USER}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON appdb.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
SQL
"

info "Redis：监听 0.0.0.0 + 密码，供本机 start-dev.sh"
"${SSH[@]}" "$HOST" "set -e
  redis_cnf=/etc/redis/redis.conf
  sed -i 's/^bind .*/bind 0.0.0.0/' \"\$redis_cnf\"
  if grep -qE '^requirepass ' \"\$redis_cnf\"; then
    sed -i 's/^requirepass .*/requirepass ${REDIS_PASS}/' \"\$redis_cnf\"
  elif grep -qE '^# requirepass ' \"\$redis_cnf\"; then
    sed -i 's/^# requirepass .*/requirepass ${REDIS_PASS}/' \"\$redis_cnf\"
  else
    printf '\nrequirepass ${REDIS_PASS}\n' >> \"\$redis_cnf\"
  fi
  systemctl restart redis-server
  redis-cli -a '${REDIS_PASS}' --no-auth-warning ping
"

info "导入空库表结构"
"${SSH[@]}" "$HOST" "mkdir -p /tmp/alchemy-sql"
"${SCP[@]}" \
  "$ROOT/sql/ry_20260417.sql" \
  "$ROOT/sql/stock_market_cache.sql" \
  "$ROOT/sql/quartz.sql" \
  "$ROOT/sql/patch_drop_code_gen.sql" \
  "$ROOT/sql/patch_member_menu_stock_list.sql" \
  "$ROOT/sql/patch_disable_captcha.sql" \
  "$HOST:/tmp/alchemy-sql/"
"${SSH[@]}" "$HOST" "set -e
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/ry_20260417.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/stock_market_cache.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/quartz.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/patch_drop_code_gen.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/patch_member_menu_stock_list.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb < /tmp/alchemy-sql/patch_disable_captcha.sql
  mysql --protocol=socket -u ${MYSQL_USER} -p'${MYSQL_PASS}' appdb -N -e 'SELECT COUNT(*) FROM sys_user; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=\"appdb\";'
  rm -rf /tmp/alchemy-sql
"

ok "首次环境就绪。下一步：./deploy/release.sh 然后 ./deploy/apply-nginx.sh"
