import json
import os
import os.path
import pathlib
import subprocess
import sys
import threading
from subprocess import Popen, PIPE

import click
import hcl
from rich import pretty
from rich import print

from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, Fargate, ElasticContainerService, \
    EC2ContainerRegistry
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB, VPC
from diagrams.aws.network import Route53
from diagrams.aws.security import SecretsManager, ACM
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch


class LocalShell(object):
    def __init__(self):
        pass

    def run(self, command):
        env = os.environ.copy()
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT,
                  shell=True, env=env)

        def writeall(p):
            while True:
                # print("read data: ")
                data = p.stdout.read(1).decode("utf-8")
                if not data:
                    break
                sys.stdout.write(data)
                sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(p,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                self._write(p, d.encode())

        except EOFError:
            pass

    def _write(self, process, message):
        process.stdin.write(message)
        process.stdin.flush()


@click.group()
def cli():
    """
    Interact with the container install
    """
    pass


@click.command()
def get_aws_id():
    """
    Get the AWS ID for the current user
    """
    print(_get_aws_id())


@click.command()
def get_prefix():
    """
    Get the prefix for this install
    """
    print(_get_prefix())


@click.command()
def get_region():
    """
    Get the region we're in
    """
    print(_get_region())


@click.command()
def get_task():
    """
    Get the task ID for our service
    """
    print(_get_task())


@click.command()
def shell_app():
    """
    Drop to a shell on the gunicorn container
    """
    _shell_app()


@click.command()
def shell_nginx():
    """
    Drop to a shell on the nginx container
    """
    _shell_app('django_nginx')


@click.command()
def docker_login():
    """
    Get a login token from AWS ECR
    """
    _get_docker()


@click.command()
def update_build():
    """
    Update the build file with the Docker registry
    """
    _update_build()


def _get_docker():
    command = 'aws ecr get-login-password --region {0} | docker ' \
              'login --username AWS --password-stdin ' \
              '{1}.dkr.ecr.{0}.amazonaws.com'.format(_get_region(),
                                                     _get_aws_id())

    result = subprocess.check_output(command, shell=True).decode('utf-8')

    return result


def _update_build():
    build_file = pathlib.Path('build.sh')

    registry = 'export DOCKER_REGISTRY={0}.dkr.ecr.{1}.' \
               'amazonaws.com\n'.format(_get_aws_id(), _get_region())

    with build_file.open('w') as out_file:
        out_file.write('#!/bin/bash\n')
        out_file.write(registry)
        out_file.write('docker-compose build\n')
        out_file.write('docker-compose push\n')


def _shell_app(container='django_python'):
    task = _parse_task()

    if not task:
        return

    command = '/usr/local/bin/aws ecs execute-command ' \
              '--cluster martinpauleve-test ' \
              '--container {} --interactive ' \
              '--command "/bin/sh" --task {}'.format(container, task)

    print('Executing: {}'.format(command))

    shell = LocalShell()
    shell.run(command)


def _parse_task():
    task = _get_task()

    if not task:
        print('No running tasks found')
        return task

    task = task.split('/')[-1]
    return task


def _get_task():
    command = '/usr/local/bin/aws ecs list-tasks --cluster ' \
              'arn:aws:ecs:{0}:{1}:cluster/{2} ' \
              '--service-name {2}-service'.format(_get_region(), _get_aws_id(),
                                                  _get_prefix())

    result = subprocess.check_output(command.split(' ')).decode('utf-8')

    dict_res = json.loads(result)

    if 'taskArns' not in dict_res or len(dict_res['taskArns']) == 0:
        return None

    return dict_res['taskArns'][0]


def _get_aws_id():
    # Get the AWS username
    result = subprocess.check_output(
        'aws sts get-caller-identity --query '
        '"Account"'.split(' ')).decode('utf-8')

    result = str(result).replace('"', '')
    result = str(result).replace('\n', '')
    return result


def _get_prefix():
    with open("AWS/terraform.tfvars", "r") as f:
        data = hcl.load(f)
        return _get_terraform_config()['name_prefix']


def _get_region():
    result = subprocess.check_output(
        'aws configure get region'.split(' ')).decode('utf-8')

    result = str(result).replace('\n', '')
    return str(result)


def _get_terraform_config():
    with open("AWS/terraform.tfvars", "r") as f:
        data = hcl.load(f)
        return data


@click.command()
def generate_diagram():
    """
    Draw the infrastructure diagram
    """

    with Diagram("Containerized Django on AWS", show=True):
        dns = Route53("DNS")

        with Cluster("VPC"):
            lb = ELB("Load Balancer")
            vpc = VPC()

            with Cluster("Elastic Container Services"):
                svc_group = [Fargate("ECS HTTP"), Fargate("ECS HTTPS")]

            with Cluster("Container Registry"):
                registry = [EC2ContainerRegistry("Django (Gunicorn)"),
                            EC2ContainerRegistry("Nginx")]

            with Cluster("DB Cluster"):
                db_primary = RDS("Aurora Postgres")

        with Cluster("Storage"):
            storage = S3("S3 Log Storage")

        with Cluster("Secrets"):
            secrets = SecretsManager("Secret Manager")

        with Cluster("Cloudwatch"):
            cloud_watch = Cloudwatch("Alarms")


        cert = ACM("SSL Certificate")

        dns >> lb >> svc_group
        svc_group >> registry[1] >> registry[0] >> secrets >> db_primary
        registry >> cloud_watch >> storage
        db_primary >> cloud_watch
        lb >> cloud_watch
        db_primary >> registry
        lb >> cert



if __name__ == '__main__':
    pretty.install()
    cli.add_command(get_aws_id)
    cli.add_command(get_prefix)
    cli.add_command(get_region)
    cli.add_command(get_task)
    cli.add_command(shell_app)
    cli.add_command(shell_nginx)
    cli.add_command(docker_login)
    cli.add_command(update_build)
    cli.add_command(generate_diagram)
    cli()
