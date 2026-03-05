#!/usr/bin/python3
import sys

retf = sys.argv[-1]
data = {}
for f in sys.argv[1:-1]:
    with open(f, 'r') as f:
        for line in f.read().split('\n'):
            try:
                k, v = line.split('=', 1)
                data[k] = v
            except Exception:
                pass

if sys.argv[0].endswith('owebui_postgresql_env_post'):
    import os
    import time
    import shutil
    import subprocess

    env = os.environ.copy()
    env["PGPASSWORD"] = data['POSTGRES_PASSWORD']

    psql_cmd = shutil.which('psql')

    found = False

    for i in range(20):
        p = subprocess.run([psql_cmd, '-U', data['POSTGRES_USER'], '-h',  data['POSTGRES_HOST'],
                    '-p', data['POSTGRES_PORT'], data['POSTGRES_DB'], "-c", 'SELECT * FROM pg_extension;'],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if p.returncode != 0:
            time.sleep(0.5)
        else:
            for line in p.stdout.split('\n'):
                if 'vector' in line:
                    found = True
                    break
            break
    else:
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

    if found is False:
        p = subprocess.run([psql_cmd, '-U', data['POSTGRES_USER'],
                '-h',  data['POSTGRES_HOST'], '-p', data['POSTGRES_PORT'], data['POSTGRES_DB'],
                "-c", 'CREATE EXTENSION IF NOT EXISTS "vector";'],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(3)

elif sys.argv[0].endswith('owebui_postgresql_env_pre'):
    with open(retf, 'w') as f:
        if ("POSTGRES_HOST" not in data or data['POSTGRES_HOST'] == "") and \
          ("POSTGRES_PORT" not in data or data['POSTGRES_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("POSTGRES_HOST" not in data or data['POSTGRES_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:5432"\n' % data['POSTGRES_PORT'])
        elif ("POSTGRES_PORT" not in data or data['POSTGRES_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:5432:5432"\n' % data['POSTGRES_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:5432"\n' % (data['POSTGRES_HOST'], data['POSTGRES_PORT']))

elif sys.argv[0].endswith('owebui_postgresql_env_cond'):
    import shutil
    import subprocess

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['POSTGRES_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['POSTGRES_IMAGE']), file=sys.stderr)
        sys.exit(1)
