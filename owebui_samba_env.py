#!/usr/bin/python3
import sys

if sys.argv[0].endswith('owebui_samba_env_post'):
    pass

elif sys.argv[0].endswith('owebui_samba_env_pre'):
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, dockerenv = parse_files(sys.argv[1:-1], "samba")

    with open(retf, 'w') as f:
        if ("SAMBA_HOST" not in data or data['SAMBA_HOST'] == "") and \
          ("SAMBA_PORT_DS" not in data or data['SAMBA_PORT_DS'] == ""):
            f.write("PORTMAP_CMD_DS=\n")
            f.write("PORTMAP_ARG_DS=\n")
        elif ("SAMBA_HOST" not in data or data['SAMBA_HOST'] == ""):
            f.write("PORTMAP_CMD_DS=-p\n")
            f.write('PORTMAP_ARG_DS="%s:445"\n' % data['SAMBA_PORT_DS'])
        elif ("SAMBA_PORT_DS" not in data or data['SAMBA_PORT_DS'] == ""):
            f.write("PORTMAP_CMD_DS=-p\n")
            f.write('PORTMAP_ARG_DS="%s:445:445"\n' % data['SAMBA_HOST'])
        else:
            f.write("PORTMAP_CMD_DS=-p\n")
            f.write('PORTMAP_ARG_DS="%s:%s:445"\n' % (data['SAMBA_HOST'], data['SAMBA_PORT_DS']))
        if ("SAMBA_HOST" not in data or data['SAMBA_HOST'] == "") and \
          ("SAMBA_PORT_SSN" not in data or data['SAMBA_PORT_SSN'] == ""):
            f.write("PORTMAP_CMD_SSN=\n")
            f.write("PORTMAP_ARG_SSN=\n")
        elif ("SAMBA_HOST" not in data or data['SAMBA_HOST'] == ""):
            f.write("PORTMAP_CMD_SSN=-p\n")
            f.write('PORTMAP_ARG_SSN="%s:139"\n' % data['SAMBA_PORT_SSN'])
        elif ("SAMBA_PORT_SSN" not in data or data['SAMBA_PORT_SSN'] == ""):
            f.write("PORTMAP_CMD_SSN=-p\n")
            f.write('PORTMAP_ARG_SSN="%s:139:139"\n' % data['SAMBA_HOST'])
        else:
            f.write("PORTMAP_CMD_SSN=-p\n")
            f.write('PORTMAP_ARG_SSN="%s:%s:139"\n' % (data['SAMBA_HOST'], data['SAMBA_PORT_SSN']))


elif sys.argv[0].endswith('owebui_samba_env_cond'):
    import shutil
    import subprocess
    from owebui_tools import parse_files

    retf = sys.argv[-1]
    data, _ = parse_files(sys.argv[1:-1], "samba")

    docker_cmd = shutil.which('docker')

    p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", data['SAMBA_IMAGE']], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Can't find docker image %s. Delayed start" % (data['SAMBA_IMAGE']), file=sys.stderr)
        sys.exit(1)

