# poetry run celery  -A ori_v2 worker -l INFO
# poetry run watchmedo auto-restart -- directory-d ori_v2/ -p '*.py' -- celery -A ori_v2 worker -l INFO

poetry run -- watchmedo auto-restart --directory ori_v2/ --pattern '*.py' --recursive -- celery -A ori_v2 worker -l WARNING