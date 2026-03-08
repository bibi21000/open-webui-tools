#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_app_env_post'):
    pass


elif sys.argv[0].endswith('owebui_app_env_pre'):
    import os
    import subprocess
    import shutil
    from owebui_tools import get_container_ip, parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "app")

    docker_cmd = shutil.which('docker')

    if ("POSTGRES_HOST" not in data or data['POSTGRES_HOST'] == "" or data['POSTGRES_HOST'] == "127.0.0.1"):
        pgip = get_container_ip("owebui_postgresql", docker_cmd=docker_cmd, time_out=10)
        pgport = 5432
    else:
        pgip = data['POSTGRES_HOST']
        if ("POSTGRES_PORT" not in data or data['POSTGRES_PORT'] == ""):
            pgport = 5432
        else:
            pgport = data['POSTGRES_PORT']

    if ("OLLAMA_HOST" not in data or data['OLLAMA_HOST'] == "" or data['OLLAMA_HOST'] == "127.0.0.1"):
        olip = get_container_ip("owebui_ollama", docker_cmd=docker_cmd, time_out=10)
        olport = 11434
    else:
        olip = data['OLLAMA_HOST']
        if ("OLLAMA_PORT" not in data or data['OLLAMA_PORT'] == ""):
            olport = 11434
        else:
            olport = data['OLLAMA_PORT']

    with open(retf, 'w') as f:
        if ("OWEBUI_HOST" not in data or data['OWEBUI_HOST'] == "") and \
          ("OWEBUI_PORT" not in data or data['OWEBUI_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("OWEBUI_HOST" not in data or data['OWEBUI_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:8080\n' % data['OWEBUI_PORT'])
        elif ("OWEBUI_PORT" not in data or data['OWEBUI_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:8080:8080\n' % data['OWEBUI_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:8080"\n' % (data['OWEBUI_HOST'], data['OWEBUI_PORT']))
        docker_db = f"DATABASE_URL=postgresql://{data['POSTGRES_USER']}:{data['POSTGRES_PASSWORD']}@{pgip}:{pgport}/{data['POSTGRES_DB']}"
        f.write(docker_db + '\n')
        docker_pgv = f"PGVECTOR_DB_URL=postgresql://{data['POSTGRES_USER']}:{data['POSTGRES_PASSWORD']}@{pgip}:{pgport}/{data['POSTGRES_DB']}"
        f.write(docker_pgv + '\n')
        docker_ol = f"OLLAMA_BASE_URL=http://{olip}:{olport}"
        sdockerenv = f"-e {docker_db} -e {docker_ol} "
        f.write(docker_ol + '\n')
        if 'VECTOR_DB' in dockerenv:
            sdockerenv += f"-e {docker_pgv} "
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"OWEBUI_ENV={sdockerenv}\n")
    os.chmod(retf, 0o640)


elif sys.argv[0].endswith('owebui_app_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "app")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['OWEBUI_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['OWEBUI_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_app_env_upgrade'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    data, _ = parse_files(['/etc/open-webui/open-webui-app.conf',
            '/etc/default/open_webui',
            '/etc/open-webui/open-webui-local.conf'], "app")
    if 'OWEBUI_IMAGE_SRC' not in data or 'OWEBUI_IMAGE_PKGS' not in data:
        sys.exit(0)

    image_id = sys.argv[1]

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'rm', '*f', "owebui_app_upgrade"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pkgs = data['OWEBUI_IMAGE_PKGS'].strip('"').strip("'")
    cmd = f"apt-get update && \
        apt-get install -y --no-install-recommends {pkgs} \
        && rm -rf /var/lib/apt/lists/*"
    p = subprocess.run([docker_cmd, 'run', '--name', 'owebui_app_upgrade', data['OWEBUI_IMAGE_SRC'],
        "bash", "-c", cmd],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't install package in %s for image %s" % ('owebui_app_upgrade', image_id), file=sys.stderr)
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(1)

    p = subprocess.run([docker_cmd, 'commit', '--change', 'CMD ["bash", "start.sh"]',
        'owebui_app_upgrade', data['OWEBUI_IMAGE']],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't commit %s in %s" % ('owebui_app_upgrade', data['OWEBUI_IMAGE']), file=sys.stderr)
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

    p = subprocess.run([docker_cmd, 'rm', "owebui_app_upgrade"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
