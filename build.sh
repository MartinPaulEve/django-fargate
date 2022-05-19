#!/bin/bash
export DOCKER_REGISTRY=747101050174.dkr.ecr.us-east-1.amazonaws.com
docker-compose build
docker-compose push
