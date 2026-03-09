#!/usr/bin/python3
import os
import sys
import shutil
import subprocess
import click
from owebui_tools import parse_files


SRVS = [ ('postgresql', 'POSTGRES_IMAGE', 'owebui_postgresql'),
          ('ollama', 'OLLAMA_IMAGE', 'owebui_ollama'),
          ('app', 'OWEBUI_IMAGE', 'owebui_app'),
          ('caddy', 'CADDY_IMAGE', 'owebui_caddy'),
          ('samba', 'SAMBA_IMAGE', 'owebui_samba'),
          ('docling', 'DOCLING_IMAGE', 'owebui_docling'),
        ]

def complete_servers(ctx, param, incomplete):
    if incomplete == "":
        return [' '] + [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]) is True]
    else:
        return [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]) is True]

def complete_update(ctx, param, incomplete):
    opts = ['--force', '--models', '--restart']
    if incomplete == "":
        return opts + [' '] + [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]) is True]
    elif incomplete.startswith('-'):
        return [opt for opt in opts if opt.startswith(incomplete) and opt not in incomplete]
    else:
        return [srv[0] for srv in SRVS if srv[0].startswith(incomplete) and os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]) is True]

@click.group()
def cli():
    pass

@cli.command()
def status():
    """Show open-webui services status"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'is-active', "open-webui-%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("open-webui-%s : %s" %(srv[0], p.stdout.split('\n')[0]), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def start(service):
    """Start open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'is-active', "open-webui-%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if p.stdout.split('\n')[0] == 'inactive' or p.stdout.split('\n')[0] == 'failed':
                p = subprocess.run([systemctl_cmd,'start', "open-webui-%s.service"%srv[0]],
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                print("Started open-webui-%s" %(srv[0]), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def stop(service):
    """Stop open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'stop', "open-webui-%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Stopped open-webui-%s" %(srv[0]), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def restart(service):
    """Restart open-webui services"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'restart', "open-webui-%s.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Restarted open-webui-%s" %(srv[0]), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def env(service):
    """Get env of open-webui services"""
    docker_cmd = shutil.which('docker')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):
            print("Environment of open-webui-%s : " %(srv[0]), flush=True)
            p = subprocess.run([docker_cmd,'exec', '-it', srv[2], 'env'],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                for err in p.stderr.split('\n'):
                    if err != '':
                        print('%s' % (err), file=sys.stderr)
            else:
                for line in p.stdout.split('\n'):
                    print('   ' + line.strip(), flush=True)
            print(flush=True)

@cli.command()
@click.argument('service', shell_complete=complete_servers)
@click.argument('command')
def exec(service, command):
    """Exec command in open-webui service"""
    docker_cmd = shutil.which('docker')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):
            print("Exec %s in open-webui-%s : " %(command, srv[0]), flush=True)
            p = subprocess.run([docker_cmd,'exec', '-it', srv[2]] + command.split(" "),
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                for err in p.stderr.split('\n'):
                    if err != '':
                        print('%s' % (err), file=sys.stderr)
            else:
                for line in p.stdout.split('\n'):
                    print('   ' + line.strip(), flush=True)



@cli.command()
@click.option('--force', is_flag=True, help="Force update of the image")
@click.option('--models', is_flag=True, help="Also update ollama models")
@click.option('--restart', is_flag=True, help="Start or restart services after update")
@click.argument('service', default=None, required=False, shell_complete=complete_update)
def update(force, models, restart, service):
    """Update docker images"""
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):
            print("Update %s for open-webui-%s" % (srv[1], srv[0]), flush=True)
            data, _ = parse_files(['/etc/open-webui/open-webui-%s.conf' % srv[0],
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
            if srv[1] + '_LARGE' in data:
                cmd.append(data[srv[1] + '_LARGE'])
            p = subprocess.run(cmd, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in p.stdout.split('\n'):
                print(line.strip(), flush=True)

            if p.returncode != 0:
                for err in p.stderr.split('\n'):
                    if err != '':
                        print('%s' % (err), file=sys.stderr)

            if models and srv[0] == 'open-webui-ollama':
                print("Install ollama models", flush=True)
                olama_check()
                print(flush=True)

@cli.command()
def ps():
    """List running containers"""
    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'ps', "--all"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in p.stdout.split('\n'):
        if 'owebui_' in line:
            print(line.strip(), flush=True)

@cli.command()
def update_status():
    """Show open-webui update timers and services status"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            ps = subprocess.run([systemctl_cmd,'is-active', "open-webui-%s-update.service"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pt = subprocess.run([systemctl_cmd,'is-active', "open-webui-%s-update.timer"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pts = pt.stdout.split('\n')[0]
            if pts == 'active':
                pd = subprocess.run([systemctl_cmd,'status', '--no-pager', "open-webui-%s-update.timer"%srv[0]],
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for line in pd.stdout.split('\n'):
                    if 'Active: active' in line:
                        last = " - Last run at %s" % line.split('since')[1].strip()
                        break
                else:
                    last = " - Last run not founs"
            else:
                last = ""
            print("open-webui-%s : %s (%s)%s" %(srv[0], pts, ps.stdout.split('\n')[0], last), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def update_enable(service):
    """Enable open-webui update timers"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'is-active', "open-webui-%s-update.timer"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if p.stdout.split('\n')[0] == 'inactive':
                p = subprocess.run([systemctl_cmd,'start', "open-webui-%s-update.timer"%srv[0]],
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                print("Started open-webui-%s-update timer" %(srv[0]), flush=True)

@cli.command()
@click.argument('service', default=None, required=False, shell_complete=complete_servers)
def update_disable(service):
    """Disable open-webui update timers"""
    systemctl_cmd = shutil.which('systemctl')
    for srv in SRVS:
        if service is not None and service != srv[0]:
            continue
        if os.path.exists('/etc/open-webui/open-webui-%s.conf' % srv[0]):

            p = subprocess.run([systemctl_cmd,'stop', "open-webui-%s-update.timer"%srv[0]],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Stopped open-webui-%s-update timer" %(srv[0]), flush=True)

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
                print("Install model %s" % (model), flush=True)
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
            print(line.strip(), flush=True)

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
            print(line.strip(), flush=True)

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
            print(line.strip(), flush=True)

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
            print(line.strip(), flush=True)

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
            print(line.strip(), flush=True)

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
