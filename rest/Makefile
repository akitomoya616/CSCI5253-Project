VERSION=v1
DOCKERUSER = sitonglu

build:
	docker build -f Dockerfile -t project-rest .

push:
	docker tag project-rest $(DOCKERUSER)/project-rest:$(VERSION)
	docker push $(DOCKERUSER)/project-rest:$(VERSION)
	docker tag project-rest $(DOCKERUSER)/project-rest:latest
	docker push $(DOCKERUSER)/project-rest:latest
