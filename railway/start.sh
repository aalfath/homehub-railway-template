#!/bin/sh
# Start HomeHub on Railway: keep its data on the volume, lock it with the generated
# passwords before the port opens, then run gunicorn on $PORT.
set -eu

DATA="${HOMEHUB_DATA_DIR:-/data}"
PORT="${PORT:-5000}"

fail() { echo "homehub-railway: $*" >&2; exit 1; }

# Never open HomeHub without its site password: refuse to start instead.
site_pw="${HOMEHUB_SITE_PASSWORD:-}"; admin_pw="${HOMEHUB_ADMIN_PASSWORD:-}"
[ "${#site_pw}" -ge 12 ] || fail "HOMEHUB_SITE_PASSWORD must be set (12+ characters). HomeHub has no other login, so it will not start without it."
[ "${#admin_pw}" -ge 12 ] || fail "HOMEHUB_ADMIN_PASSWORD must be set (12+ characters)."

mkdir -p "$DATA/data" "$DATA/uploads" "$DATA/media" "$DATA/pdfs" || fail "cannot write to $DATA (is the volume attached?)"
for d in data uploads media pdfs; do
  if [ -e "/app/$d" ] && [ ! -L "/app/$d" ]; then
    # Anything the image ships there (normally nothing) moves to the volume once
    cp -an "/app/$d/." "$DATA/$d/" 2>/dev/null || true
    rm -r "/app/$d"
  fi
  ln -sfn "$DATA/$d" "/app/$d"
done
ln -sfn "$DATA/config.yml" /app/config.yml

# Write or update config.yml and the admin password (exits non-zero on any problem)
cd /app
python /railway/configure.py

# Size the thread pool from the service's CPU limit, not the host's
THREADS="${GUNICORN_THREADS:-}"
if [ -z "$THREADS" ]; then
  THREADS=4
  if [ -r /sys/fs/cgroup/cpu.max ]; then
    read -r quota period < /sys/fs/cgroup/cpu.max || true
    if [ "${quota:-max}" != "max" ] && [ -n "${period:-}" ]; then
      cpus=$(( (quota + period - 1) / period ))
      THREADS=$(( cpus * 4 )); [ "$THREADS" -lt 4 ] && THREADS=4; [ "$THREADS" -gt 16 ] && THREADS=16
    fi
  fi
fi

# One worker on purpose: SQLite and HomeHub's in-process locks need a single process (see upstream Dockerfile).
exec gunicorn --chdir /app --pythonpath /railway railway_wsgi:app \
  -w 1 -k gthread --threads "$THREADS" -b "0.0.0.0:${PORT}" --error-logfile - --timeout 120
