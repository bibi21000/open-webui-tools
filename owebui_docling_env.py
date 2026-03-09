#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_docling_env_post'):
    pass

elif sys.argv[0].endswith('owebui_docling_env_pre'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "docling")

    with open(retf, 'w') as f:
        if ("DOCLING_HOST" not in data or data['DOCLING_HOST'] == "") and \
          ("DOCLING_PORT" not in data or data['DOCLING_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("DOCLING_HOST" not in data or data['DOCLING_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:5001"\n' % data['DOCLING_PORT'])
        elif ("DOCLING_PORT" not in data or data['DOCLING_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:5001:5001"\n' % data['DOCLING_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:5001"\n' % (data['DOCLING_HOST'], data['DOCLING_PORT']))
        sdockerenv = f""
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"DOCLING_ENV={sdockerenv}\n")
    os.chmod(retf, 0o640)


elif sys.argv[0].endswith('owebui_docling_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "docling")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['DOCLING_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['DOCLING_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_docling_env_upgrade'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    data, _ = parse_files(['/etc/open-webui/open-webui-docling.conf',
            '/etc/default/open_webui',
            '/etc/open-webui/open-webui-local.conf'], "docling")
    if 'DOCLING_IMAGE_SRC' not in data \
      or 'DOCLING_IMAGE_LANGS' not in data or \
      data['DOCLING_IMAGE_LANGS'] == "" :
        sys.exit(0)

    image_id = sys.argv[1]

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'rm', '*f', "owebui_docling_upgrade"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    langs = data['DOCLING_IMAGE_LANGS'].strip('"').strip("'")
    cmd = ""
    for lang in langs.split(','):
        cmd += f"curl -L https://github.com/tesseract-ocr/tessdata/raw/main/{lang}.traineddata -o /usr/share/tesseract/tessdata/{lang}.traineddata && "
    cmd += "chmod 644 /usr/share/tesseract/tessdata/*.traineddata"
    p = subprocess.run([docker_cmd, 'run', '--user', '0', '--name', 'owebui_docling_upgrade', data['DOCLING_IMAGE_SRC'],
        "bash", "-c", cmd],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't install langs in %s for image %s" % ('owebui_docling_upgrade', image_id), file=sys.stderr)
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(1)

    p = subprocess.run([docker_cmd, 'commit', '--change', 'CMD ["docling-serve", "run"]',
        'owebui_docling_upgrade', data['DOCLING_IMAGE']],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't commit %s in %s" % ('owebui_docling_upgrade', data['DOCLING_IMAGE']), file=sys.stderr)
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(2)

    p = subprocess.run([docker_cmd, 'rm', "owebui_docling_upgrade"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


elif sys.argv[0].endswith('owebui_docling_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "docling")

    if 'DOCLING_DEBUG' not in data or data['DOCLING_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
