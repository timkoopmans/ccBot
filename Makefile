.PHONY: list
SHELL := /bin/bash
export DOCKER_BUILDKIT=1

list:
	@awk -F: '/^[A-z]/ {print $$1}' Makefile | sort

_ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

build:
	docker compose build
	kind load docker-image timkoopmans/ccbot:latest --name home


deploy:
	kubectl apply -f ccbot.yaml

replace:
	kubectl get pod ccbot -o yaml | kubectl replace --force -f -