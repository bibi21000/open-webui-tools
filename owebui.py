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
        ]

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
@click.argument('service', default=None, required=False)
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
@click.argument('service', default=None, required=False)
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
def update():
    """Update docker images"""
    for srv in SRVS:
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

if __name__ == '__main__':
    cli()
