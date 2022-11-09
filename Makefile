
go: docker-up init-db


docker-up:
	docker compose up -d

init-db:
	docker exec auth_api bash -c ". /app/init_api.sh"

