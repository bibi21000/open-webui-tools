#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_goaccess_env_post'):
    pass

elif sys.argv[0].endswith('owebui_goaccess_env_pre'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "goaccess")

    with open(retf, 'w') as f:
        sdockercmd = "/usr/bin/docker run --name owebui_goaccess --rm"
        if "OWEBUI_DOCKER_OPTS" in data and data["OWEBUI_DOCKER_OPTS"] := "":
            sdockercmd += " %s" % data["OWEBUI_DOCKER_OPTS"]
        sdockerenv = f""
        scmdenv = "--log-file=/logs/access.log --log-format=CADDY " + \
                  "--db-path=/db --persist --restore --real-time-html --output=/www/index.html"

        if ("GOACCESS_HOST" not in data or data['GOACCESS_HOST'] == "") and \
          ("GOACCESS_PORT" not in data or data['GOACCESS_PORT'] == ""):
            f.write("PORTMAP_CMD=\n")
            f.write("PORTMAP_ARG=\n")
        elif ("GOACCESS_HOST" not in data or data['GOACCESS_HOST'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:7890"\n' % data['GOACCESS_PORT'])
            sdockercmd += f" -p {data['GOACCESS_PORT']}:7890"
        elif ("GOACCESS_PORT" not in data or data['GOACCESS_PORT'] == ""):
            f.write("PORTMAP_CMD=-p\n")
            f.write('PORTMAP_ARG="%s:7890:7890"\n' % data['GOACCESS_HOST'])
            sdockercmd += f" -p {data['GOACCESS_HOST']}:7890:7890"
        else:
            f.write('PORTMAP_ARG="%s:%s:7890"\n' % (data['GOACCESS_HOST'], data['GOACCESS_PORT']))
            sdockercmd += f" -p {data['GOACCESS_HOST']}:{data['GOACCESS_PORT']}:7890"

        sdockercmd += f" -v {data['OWEBUI_GOACCESS']}/db:/db"
        sdockercmd += f" -v {data['OWEBUI_GOACCESS']}/stats:/www"
        sdockercmd += f" -v {data['OWEBUI_CADDY']}/logs:/logs"

        if os.path.exists('/etc/open-webui/open-webui-maxmind.conf'):
            f.write("VOL_MAXMIND_CMD=-v\n")
            f.write("VOL_MAXMIND=%s:/maxmind:ro\n" % data['OWEBUI_MAXMIND'])
            f.write("GOACCESS_CMD8=--geoip-database=/maxmind/GeoLite2-City.mmdb\n")
            scmdenv += " --geoip-database=/maxmind/GeoLite2-City.mmdb"
            sdockercmd += f" -v {data['OWEBUI_MAXMIND']}:/maxmind:ro"

        for ev in dockerenv:
            sdockerenv += f'-e {ev}={dockerenv[ev]} '
        f.write(f'GOACCESS_ENV="{sdockerenv}"\n')

        if "GOACCESS_URL" in data:
            scmdenv += f" --ws-url=wss://{data['GOACCESS_URL']}:443"
            f.write(f"GOACCESS_CMD9=--ws-url=wss://{data['GOACCESS_URL']}:443\n")

        f.write(f'GOACCESS_CMD="{scmdenv}\"n')
        f.write("GOACCESS_CMD1=--log-file=/logs/access.log\n")
        f.write("GOACCESS_CMD2=--log-format=CADDY\n")
        f.write("GOACCESS_CMD3=--db-path=/db\n")
        f.write("GOACCESS_CMD4=--persist\n")
        f.write("GOACCESS_CMD5=--restore\n")
        f.write("GOACCESS_CMD6=--real-time-html\n")
        f.write("GOACCESS_CMD7=--output=/www/index.html\n")

        sdockercmd += f" {sdockerenv}"
        sdockercmd += f" {data['GOACCESS_IMAGE']}"
        sdockercmd += f" {scmdenv}"
        f.write(f"GOACCESS_RUN={sdockercmd}\n")

    os.chmod(retf, 0o640)


elif sys.argv[0].endswith('owebui_goaccess_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "goaccess")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['GOACCESS_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['GOACCESS_IMAGE']), file=sys.stderr)
        sys.exit(1)


elif sys.argv[0].endswith('owebui_goaccess_env_stop'):
    import os
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "goaccess")

    if 'GOACCESS_DEBUG' not in data or data['GOACCESS_DEBUG'] != 'true':
        retf = sys.argv[-1]
        if os.path.exists(retf):
            os.remove(retf)
