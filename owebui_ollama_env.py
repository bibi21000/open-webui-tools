#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_ollama_env_post'):
    pass

elif sys.argv[0].endswith('owebui_ollama_env_pre'):
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "ollama")

    with open(retf, 'w') as f:
        if ("OLLAMA_HOST" not in data or data['OLLAMA_HOST'] == "") and \
          ("OLLAMA_PORT" not in data or data['OLLAMA_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("OLLAMA_HOST" not in data or data['OLLAMA_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:11434"\n' % data['OLLAMA_PORT'])
        elif ("OLLAMA_PORT" not in data or data['OLLAMA_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:11434:11434"\n' % data['OLLAMA_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:11434"\n' % (data['OLLAMA_HOST'], data['OLLAMA_PORT']))


elif sys.argv[0].endswith('owebui_ollama_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "ollama")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['OLLAMA_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['OLLAMA_IMAGE']), file=sys.stderr)
        sys.exit(1)


