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

if sys.argv[0].endswith('owebui_ollama_env_post'):
    pass

elif sys.argv[0].endswith('owebui_ollama_env_pre'):
    with open(retf, 'w') as f:
        if ("OLLAMA_HOST" not in data or data['OLLAMA_HOST'] == "") and \
          ("OLLAMA_PORT" not in data or data['OLLAMA_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("OLLAMA_HOST" not in data or data['OLLAMA_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:5432"\n' % data['OLLAMA_PORT'])
        elif ("OLLAMA_PORT" not in data or data['OLLAMA_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:11434:11434"\n' % data['OLLAMA_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:11434"\n' % (data['OLLAMA_HOST'], data['OLLAMA_PORT']))


elif sys.argv[0].endswith('owebui_ollama_env_cond'):
    import shutil
    import subprocess

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['OLLAMA_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['OLLAMA_IMAGE']), file=sys.stderr)
        sys.exit(1)

