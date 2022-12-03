VERSION=v5
DOCKERUSER=sitonglu

build:
	docker build -f Dockerfile -t project-worker .
push:
	docker tag project-worker $(DOCKERUSER)/project-worker:$(VERSION)
	docker push $(DOCKERUSER)/project-worker:$(VERSION)
	docker tag project-worker $(DOCKERUSER)/project-worker:latest
	docker push $(DOCKERUSER)/project-worker:latest
