#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_caddy_env_post'):
    pass


elif sys.argv[0].endswith('owebui_caddy_env_pre'):
    import os
    import subprocess
    import shutil
    from owebui_tools import get_container_ip, parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "caddy")

    docker_cmd = shutil.which('docker')

    if ("OWEBUI_HOST" not in data or data['OWEBUI_HOST'] == "" or data['OWEBUI_HOST'] == "127.0.0.1"):
        appip = get_container_ip("owebui_app", docker_cmd=docker_cmd)
        appport = '8080'
    else:
        appip = data['OWEBUI_HOST']
        if ("OWEBUI_PORT" not in data or data['OWEBUI_PORT'] == ""):
            appport = '8080'
        else:
            appport = data['OWEBUI_PORT']

    with open(retf, 'w') as f:

        if ("CADDY_HOST" not in data or data['CADDY_HOST'] == "") and \
          ("CADDY_PORT" not in data or data['CADDY_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("CADDY_HOST" not in data or data['CADDY_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:80\n' % data['CADDY_PORT'])
        elif ("CADDY_PORT" not in data or data['CADDY_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG=%s:80:80\n' % data['CADDY_HOST'])
        else:
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:%s:80"\n' % (data['CADDY_HOST'], data['CADDY_PORT']))
        if ("CADDY_HOST" not in data or data['CADDY_HOST'] == "") and \
          ("CADDY_PORT_SSL" not in data or data['CADDY_PORT_SSL'] == ""):
            f.write("PORTMAP_CMD_SSL=\n")
            f.write("PORTMAP_ARG_SSL=\n")
            f.write("PORTMAP_ARG_UDP=\n")
        elif ("CADDY_HOST" not in data or data['CADDY_HOST'] == ""):
            f.write("PORTMAP_CMD_SSL=-p\n")
            f.write('PORTMAP_ARG_SSL=%s:443\n' % data['CADDY_PORT_SSL'])
            f.write('PORTMAP_ARG_UDP=%s:443/udp\n' % data['CADDY_PORT_SSL'])
        elif ("CADDY_PORT_SSL" not in data or data['CADDY_PORT_SSL'] == ""):
            f.write("PORTMAP_CMD_SSL=-p\n")
            f.write('PORTMAP_ARG_SSL=%s:443:443\n' % data['CADDY_HOST'])
            f.write('PORTMAP_ARG_UDP=%s:443:443/udp\n' % data['CADDY_HOST'])
        else:
            f.write("PORTMAP_CMD_SSL=-p\n")
            f.write('PORTMAP_ARG_SSL="%s:%s:443"\n' % (data['CADDY_HOST'], data['CADDY_PORT_SSL']))
            f.write('PORTMAP_ARG_UDP="%s:%s:443/udp"\n' % (data['CADDY_HOST'], data['CADDY_PORT_SSL']))
        sdockerenv = f""
        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f"CADDY_ENV={sdockerenv}\n")
    os.chmod(retf, 0o640)

    with open(os.path.join(data['OWEBUI_CADDY'], 'conf', 'Caddyfile'), 'w') as f:
        with open('/etc/open-webui/Caddyfile', "r") as t:
            for line in t:
                f.write(line.replace('{APP_IP}', appip).replace('{APP_PORT}', appport))


elif sys.argv[0].endswith('owebui_caddy_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "caddy")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['CADDY_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['CADDY_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_caddy_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "caddy")

    if 'CADDY_DEBUG' not in data or data['CADDY_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
