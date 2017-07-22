all: build deploy

.PHONY: build
build:
	docker build mk-cluster -t mk-cluster
	docker build mk-worker -t mk-worker

.PHONY: deploy
deploy: build
	docker tag mk-cluster:latest 082395104119.dkr.ecr.us-west-1.amazonaws.com/mk-cluster:latest
	docker push 082395104119.dkr.ecr.us-west-1.amazonaws.com/mk-cluster:latest
	docker tag mk-worker:latest 082395104119.dkr.ecr.us-west-1.amazonaws.com/mk-worker:latest
	docker push 082395104119.dkr.ecr.us-west-1.amazonaws.com/mk-worker:latest
