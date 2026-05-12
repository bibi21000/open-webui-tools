#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_redis_env_post'):
    pass


elif sys.argv[0].endswith('owebui_redis_env_pre'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "redis")

    with open(retf, 'w') as f:
        if ("REDIS_HOST" not in data or data['REDIS_HOST'] == "") and \
          ("REDIS_PORT" not in data or data['REDIS_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("REDIS_HOST" not in data or data['REDIS_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:6379"\n' % data['REDIS_PORT'])
        elif ("REDIS_PORT" not in data or data['REDIS_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:6379:6379"\n' % data['REDIS_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:6379"\n' % (data['REDIS_HOST'], data['REDIS_PORT']))
        sdockerenv = f""
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"REDIS_ENV={sdockerenv}\n")
        os.chmod(retf, 0o640)


elif sys.argv[0].endswith('owebui_redis_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "redis")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['REDIS_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['REDIS_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_redis_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "redis")

    if 'REDIS_DEBUG' not in data or data['REDIS_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
