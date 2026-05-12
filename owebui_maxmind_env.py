#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_maxmind_env_post'):
    pass


elif sys.argv[0].endswith('owebui_maxmind_env_pre'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "maxmind")

    with open(retf, 'w') as f:
        sdockerenv = f""
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"MAXMIND_ENV={sdockerenv}\n")
    os.chmod(retf, 0o640)


elif sys.argv[0].endswith('owebui_maxmind_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "maxmind")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['MAXMIND_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['MAXMIND_IMAGE']), file=sys.stderr)
        sys.exit(1)
    if 'GEOIPUPDATE_ACCOUNT_ID' not in dockerenv or 'GEOIPUPDATE_LICENSE_KEY' not in dockerenv:
        print("Can't find id and license key for maxmind geoip database", file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_maxmind_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "maxmind")

    if 'MAXMIND_DEBUG' not in data or data['MAXMIND_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
