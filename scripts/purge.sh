# Usage: ./purge.sh

# --- Reset database ---
echo "[Resetting database]"
poetry run python ./ori_v2/db/reset.py

# --- Reset celery ---
# https://docs.celeryq.dev/en/latest/faq.html#how-do-i-purge-all-waiting-tasks
echo "[Resetting celery]"
poetry run celery -A ori_v2 purge -f

