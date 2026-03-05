# -*- encoding: utf-8 -*-
"""
open-webui-tools python library
--------------------------------------

"""
def parse_files(files, dockerapp):
    sysd = {}
    docker = {}
    dockerapp += '_'
    for f in files:
        with open(f, 'r') as f:
            for line in f.read().split('\n'):
                try:
                    k, v = line.split('=', 1)
                    if k.startswith(dockerapp):
                        docker[k.replace(dockerapp, '')] = v
                    else:
                        sysd[k] = v
                except Exception:
                    pass
    return sysd, docker

def get_container_ip(container, docker_cmd=None):
    import sys
    import subprocess
    import time

    if docker_cmd is None:
        import shutil
        docker_cmd = shutil.which('docker')

    for i in range(30):
        p = subprocess.run([docker_cmd, 'inspect', '-f',
                    "'{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
                    container],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            time.sleep(0.5)
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
