mmigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

run_testserver:
	uv run manage.py runserver
