mmigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

run_testserver:
	uv run manage.py runserver
	
run_docker:
	docker run -d -p 6379:6379 redis
