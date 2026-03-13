# -*- encoding: utf-8 -*-
"""
open-webui-tools python library
--------------------------------------

"""

def parse_files(files, dockerapp):
    import os
    import sys
    sysd = {}
    docker = {}
    dockerapp += '_'
    for f in files:
        if os.path.isfile(f) is False:
            print("Can't find %s. Ignore it." % (f), file=sys.stderr)
            continue
        with open(f, 'r') as f:
            for line in f.read().split('\n'):
                if line == "" or line.startswith("#"):
                    continue
                try:
                    k, v = line.split('=', 1)
                    if k.startswith(dockerapp):
                        docker[k.replace(dockerapp, '')] = v
                    else:
                        sysd[k] = v
                except Exception:
                    pass
    return sysd, docker

def get_container_ip(container, docker_cmd=None, time_out=10, time_sleep=0.5):
    import sys
    import subprocess
    import time

    if docker_cmd is None:
        import shutil
        docker_cmd = shutil.which('docker')

    for i in range(int(time_out / time_sleep)):
        p = subprocess.run([docker_cmd, 'inspect', '-f',
                    "'{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
                    container],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            time.sleep(time_sleep)
        else:
            ctip = p.stdout.split('\n')[0].strip("\'")
            break
    else:
        print( "Can't get ip of container %s" % (container), file=sys.stderr)
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)
    return ctip

def configure_dockerd(uploads=1, downloads=4):
    import json
    import shutil
    import subprocess

    with open('/etc/docker/daemon.json', 'r') as file:
        data = json.load(file)

    data['max-concurrent-uploads'] = uploads
    data['max-concurrent-downloads'] = downloads

    with open('/etc/docker/daemon.json', 'w') as f:
        json.dump(data, f, indent=4)

    systemctl_cmd = shutil.which('systemctl')

    p = subprocess.run([systemctl_cmd, 'restart', 'dockerd'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return 1
    return 0

