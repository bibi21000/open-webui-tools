#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_glances_env_post'):
    pass


elif sys.argv[0].endswith('owebui_glances_env_pre'):
    import os
    import subprocess
    import shutil
    from owebui_tools import get_container_ip, parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "glances")

    docker_cmd = shutil.which('docker')

    with open(retf, 'w') as f:

        if ("GLANCES_HOST" not in data or data['GLANCES_HOST'] == "") and \
          ("GLANCES_PORT" not in data or data['GLANCES_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("GLANCES_HOST" not in data or data['GLANCES_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:61208\n' % data['GLANCES_PORT'])
        elif ("GLANCES_PORT" not in data or data['GLANCES_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:61208:61208\n' % data['GLANCES_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:61208"\n' % (data['GLANCES_HOST'], data['GLANCES_PORT']))
        sdockerenv = '-e GLANCES_OPT="-w"'
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"GLANCES_ENV={sdockerenv}\n")
    os.chmod(retf, 0o640)

elif sys.argv[0].endswith('owebui_glances_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "glances")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['GLANCES_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['GLANCES_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_glances_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "glances")

    if 'GLANCES_DEBUG' not in data or data['GLANCES_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
