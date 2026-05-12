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
        if 'RAG_EMBEDDING_ENGINE' in dockerenv and \
          (dockerenv['RAG_EMBEDDING_ENGINE'] == 'ollama' or\
            dockerenv['RAG_EMBEDDING_ENGINE'] == '"ollama"' or\
            dockerenv['RAG_EMBEDDING_ENGINE'] == "'ollama'") and \
          'RAG_OLLAMA_BASE_URL' not in dockerenv:
            docker_rol = f"RAG_OLLAMA_BASE_URL=http://{olip}:{olport}"
            sdockerenv += f"-e {docker_rol} "
            f.write(docker_rol + '\n')
        if 'VECTOR_DB' in dockerenv:
            sdockerenv += f"-e {docker_pgv} "
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        if os.path.exists('/etc/open-webui/open-webui-docling.conf') or "DOCLING_HOST" in data:
            sdockerenv += "-e CONTENT_EXTRACTION_ENGINE=docling "
            if ("DOCLING_HOST" not in data or data['DOCLING_HOST'] == "" or data['DOCLING_HOST'] == "127.0.0.1"):
                dlip = get_container_ip("owebui_docling", docker_cmd=docker_cmd, time_out=10)
                dlport = 5001
            else:
                dlip = data['DOCLING_HOST']
                if ("DOCLING_PORT" not in data or data['DOCLING_PORT'] == ""):
                    dlport = 5001
                else:
                    dlport = data['DOCLING_PORT']
            sdockerenv += f'-e DOCLING_SERVER_URL={dlip}:{dlport} '
            if 'DOCLING_PARAMS' not in data or data['DOCLING_PARAMS'] == "":
                if 'DOCLING_IMAGE_LANGS' in data and data['DOCLING_IMAGE_LANGS'] != "":
                    langs = data['DOCLING_IMAGE_LANGS']
                else:
                    langs = "eng"
                sdockerenv += '''-e DOCLING_PARAMS='{"do_ocr": true, "ocr_engine": "tesseract", "ocr_lang": "%s"}' ''' % langs
            else:
                sdockerenv += f'-e DOCLING_PARAMS={data['DOCLING_PARAMS']} '
        if os.path.exists('/etc/open-webui/open-webui-redis.conf') or "REDIS_HOST" in data:
            if ("REDIS_HOST" not in data or data['REDIS_HOST'] == "" or data['REDIS_HOST'] == "127.0.0.1"):
                reip = get_container_ip("owebui_redis", docker_cmd=docker_cmd, time_out=10)
                report = 6379
            else:
                reip = data['REDIS_HOST']
                if ("REDIS_PORT" not in data or data['REDIS_PORT'] == ""):
                    report = 6379
                else:
                    report = data['REDIS_PORT']
            sdockerenv += f'-e REDIS_SERVER_URL=redis://{reip}:{report}/0 '
            sdockerenv += f'-e ENABLE_WEBSOCKET_SUPPORT=true '
            sdockerenv += f'-e WEBSOCKET_MANAGER=redis '
            sdockerenv += f'-e WEBSOCKET_REDIS_URL=redis://{reip}:{report}/1 '
            sdockerenv += f'-e REDIS_KEY_PREFIX=open-webui '

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
            '/etc/default/open-webui',
            '/etc/open-webui/open-webui-local.conf'], "app")
    if 'OWEBUI_IMAGE_SRC' not in data \
      or 'OWEBUI_IMAGE_PKGS' not in data \
      or data['OWEBUI_IMAGE_PKGS'] == "" :
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


elif sys.argv[0].endswith('owebui_app_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "app")

    if 'OWEBUI_DEBUG' not in data or data['OWEBUI_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
