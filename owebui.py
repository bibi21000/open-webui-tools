#!/usr/bin/python3
import os
import sys
import time
import shutil
import subprocess
import click


SRVS = [ ('open-webui-postgresql', 'POSTGRES_IMAGE'),
          ('open-webui-ollama', 'OLLAMA_IMAGE'),
          ('open-webui-app', 'OWEBUI_IMAGE'),
          ('open-webui-caddy', 'CADDY_IMAGE'),
          ('open-webui-samba', 'SAMBA_IMAGE'),
        ]

def complete_servers(ctx, param, incomplete):
    if incomplete == "":
        return [' '] + [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/%s.conf' % srv[0]) is True]
    else:
        return [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/%s.conf' % srv[0]) is True]

@click.group()
def cli():
    pass

@cli.command()
def status():
    """Show open-webui services status"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'is-active', "%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("%s : %s" %(srv[0], p.stdout.split('\n')[0]))

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def start(service):
    """Start open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'is-active', "%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if p.stdout.split('\n')[0] == 'inactive':
                p = subprocess.run([systemctl_cmd,'start', "%s.service"%srv[0]],
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                print("Start %s" %(srv[0]))

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def stop(service):
    """Stop open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'stop', "%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Stop %s" %(srv[0]))

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def restart(service):
    """Restart open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'restart', "%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Restart %s" %(srv[0]))

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def update(service):
    """Update docker images"""
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        print("Update %s for %s" % (srv[1], srv[0]))
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):
            data = {}
            for f in ['/etc/open-webui/%s.conf' % srv[0],
                      '/etc/default/open_webui',
                      '/etc/open-webui/open-webui-local.conf']:
                with open(f, 'r') as f:
                    for line in f.read().split('\n'):
                        try:
                            k, v = line.split('=', 1)
                            data[k] = v
                        except Exception:
                            pass
            p = subprocess.run([ "/usr/lib/open-webui-tools/owebui_docker_update",
                    data[srv[1]], srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in p.stdout.split('\n'):
                print(line.strip())

            if p.returncode != 0:
                for err in p.stderr:
                    if err != '':
                        print('%s' % (err), file=sys.stderr)

if os.path.exists('/etc/open-webui/open-webui-ollama.conf'):

    @cli.group()
    def ollama():
        pass


    @ollama.command()
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

    @ollama.command()
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

    @ollama.command()
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

    @ollama.command()
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

    @ollama.command()
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

    @ollama.command()
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
