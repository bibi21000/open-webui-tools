#!/usr/bin/python3
import sys
import time
import shutil
import subprocess
import click

IMG='owebui_ollama'
docker_cmd = shutil.which('docker')

@click.group()
def cli():
    pass

@cli.command()
@click.argument('model', default=None)
def pull(model):
    """Pull model MODEL."""
    p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'pull', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    for line in p.stdout.split('\n'):
        print(line.strip())

    if p.returncode != 0:
        for err in p.stderr:
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

@cli.command()
@click.argument('model', default=None)
def rm(model):
    """Remove model MODEL."""
    p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'rm', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    for line in p.stdout.split('\n'):
        print(line.strip())

    if p.returncode != 0:
        for err in p.stderr:
            if err != '':
                print('%s' % (err), file=sys.stderr)

@cli.command()
@click.argument('model', default=None)
def show(model):
    """Show information for model MODEL."""
    p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'show', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    for line in p.stdout.split('\n'):
        print(line.strip())

    if p.returncode != 0:
        for err in p.stderr:
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

@cli.command()
def list():
    """List models"""
    p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'list'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    for line in p.stdout.split('\n'):
        print(line.strip())

    if p.returncode != 0:
        for err in p.stderr:
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

@cli.command()
def ps():
    """List running models"""
    p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'ps'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    for line in p.stdout.split('\n'):
        print(line.strip())

    if p.returncode != 0:
        for err in p.stderr:
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

@cli.command()
@click.argument('models', default=None, required=False)
@click.option('--retries', default=10, help="How many retry to connect to ollama")
def check(models, retries):
    """Check if models (separated by ",") are installed and installs them if they are missing."""
    if models is None:
        return

    lmodels = []
    for retry in range(retries):
        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'list'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
        if p.returncode != 0:
            time.sleep(0.5)
            continue

        for line in p.stdout.split('\n'):
            lmodels.append(line.strip())
        break

    else:
        if p.returncode != 0:
            for err in p.stderr:
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(2)

    for model in models.split(","):
        for installed in lmodels:
            if model in installed:
                break
            p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'pull', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

if __name__ == '__main__':
    cli()
