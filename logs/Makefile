VERSION=v2
DOCKERUSER = sitonglu# PUT_YOUR_DOCKER_ID_HERE

#
# You should probably update the docker.io user if you update this
#

build:
	docker build -f Dockerfile -t logs  .

#
# The following make rule labels the current docker image with the version
# number specified above and also the "latest" tag. It then pushes it to
# hub.docker.io
#
push:
	docker tag logs  $(DOCKERUSER)/project-logs:$(VERSION)
	docker push $(DOCKERUSER)/project-logs:$(VERSION)
	docker tag logs  $(DOCKERUSER)/project-logs:latest
	docker push $(DOCKERUSER)/project-logs:latest