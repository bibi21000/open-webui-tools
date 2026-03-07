#!/usr/bin/python3
import os
import sys
import shutil
import subprocess
import click
from owebui_tools import parse_files


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

                print("Started %s" %(srv[0]))

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

            print("Stopped %s" %(srv[0]))

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

            print("Restarted %s" %(srv[0]))

@cli.command()
@click.option('--force', is_flag=True, help="Force update of the image")
@click.option('--models', is_flag=True, help="Also update ollama models")
@click.option('--restart', is_flag=True, help="Start or restart services after update")
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def update(force, models, restart, service):
    """Update docker images"""
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        print("Update %s for %s" % (srv[1], srv[0]))
        if os.path.exists('/etc/open-webui/%s.conf' % srv[0]):
            data, _ = parse_files(['/etc/open-webui/%s.conf' % srv[0],
                      '/etc/default/open_webui',
                      '/etc/open-webui/open-webui-local.conf'], srv[0])
            cmd = ["/usr/lib/open-webui-tools/owebui_docker_update",
                    data[srv[1]], srv[0]]
            if srv[1] + '_SRC' in data:
                cmd.append(data[srv[1] + '_SRC'])
            if force:
                cmd.append('--force')
            if restart:
                cmd.append('--restart')
            p = subprocess.run(cmd, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in p.stdout.split('\n'):
                print(line.strip())

            if p.returncode != 0:
                for err in p.stderr.split('\n'):
                    if err != '':
                        print('%s' % (err), file=sys.stderr)

            if models and srv[0] == 'open-webui-ollama':
                print("Install ollama models")
                olama_check()
                print()

@cli.command()
def ps():
    """List running containers"""
    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'ps', "--all"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in p.stdout.split('\n'):
        if 'owebui_' in line:
            print(line.strip())


if os.path.exists('/etc/open-webui/open-webui-ollama.conf'):

    IMG='owebui_ollama'

    def olama_check(models=None, retries=30):
        """Check if models (separated by ",") are installed and installs them if they are missing.
        If no model is provided, those defined in the configuration files are used.
        """
        import time

        if models is None:
            from owebui_tools import parse_files

            data, _ = parse_files(['/etc/open-webui/open-webui-ollama.conf',
                    '/etc/default/open_webui',
                    '/etc/open-webui/open-webui-local.conf'], "ollama")
            if 'OLLAMA_MODELS' in data:
                models = data['OLLAMA_MODELS']
            else:
                return 0

        docker_cmd = shutil.which('docker')

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
                for err in p.stderr.split('\n'):
                    if err != '':
                        print('%s' % (err), file=sys.stderr)
                return 2

        for model in models.split(","):
            for installed in lmodels:
                if model in installed:
                    break
            else:
                print("Install model %s" % (model))
                p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'pull', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
                if p.returncode != 0:
                    for err in p.stderr.split('\n'):
                        if err != '':
                            print('%s' % (err), file=sys.stderr)
                    return 3
        return 0

    @cli.group()
    def ollama():
        pass

    @ollama.command()
    @click.argument('model', default=None)
    def pull(model):
        """Pull model MODEL."""
        docker_cmd = shutil.which('docker')

        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'pull', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        for line in p.stdout.split('\n'):
            print(line.strip())

        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(2)

    @ollama.command()
    @click.argument('model', default=None)
    def rm(model):
        """Remove model MODEL."""
        docker_cmd = shutil.which('docker')

        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'rm', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        for line in p.stdout.split('\n'):
            print(line.strip())

        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)

    @ollama.command()
    @click.argument('model', default=None)
    def show(model):
        """Show information for model MODEL."""
        docker_cmd = shutil.which('docker')

        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'show', model], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        for line in p.stdout.split('\n'):
            print(line.strip())

        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(2)

    @ollama.command()
    def list():
        """List models"""
        docker_cmd = shutil.which('docker')

        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'list'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        for line in p.stdout.split('\n'):
            print(line.strip())

        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(2)

    @ollama.command()
    def ps():
        """List running models"""
        docker_cmd = shutil.which('docker')

        p = subprocess.run([docker_cmd, 'exec', "-it", IMG, 'ollama', 'ps'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        for line in p.stdout.split('\n'):
            print(line.strip())

        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(2)

    @ollama.command()
    @click.argument('models', default=None, required=False)
    @click.option('--retries', default=10, help="How many retry to connect to ollama")
    def check(models, retries):
        """Check if models (separated by ",") are installed and installs them if they are missing.
        If no model is provided, those defined in the configuration files are used.
        """
        ret = olama_check(models, retries)
        sys.exit(ret)


if __name__ == '__main__':
    cli()
