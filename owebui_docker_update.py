#!/usr/bin/python3
import sys
import time
import shutil
import subprocess
from owebui_tools import configure_dockerd

if len(sys.argv) > 7 or len(sys.argv) < 3:
    print('Usage : %s IMAGE SERVICE [IMAGE_SRC] [--force] [--restart] [--large]' % (sys.argv[0]), file=sys.stderr)
    exit(1)

args = list(sys.argv)

if '--force' in args:
    force = True
    args.remove('--force')
else:
    force = False

if '--restart' in args:
    restart = True
    args.remove('--restart')
else:
    restart = False

if '--large' in args:
    large = True
    args.remove('--large')
else:
    large = False

image = args[1]
service = args[2]
if len(args) == 4 and args[3] != '':
    image_src = args[3]
    image_ref = image_src
else:
    image_src = None
    image_ref = image

docker_cmd = shutil.which('docker')
systemctl_cmd = shutil.which('systemctl')

# Do nothing if not enabled
p = subprocess.run([systemctl_cmd, 'is-enabled', '--quiet', service], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0 and restart is False:
    print("Service %s is not enabled. Don't update it" % service)
    sys.exit(0)

p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", image_ref], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    current_imageid = None
    print("Image %s not found. Download it" % (image_ref))
else:
    current_imageid = p.stdout.split('\n')[0]
    print("Id for %s : %s" % (image_ref, current_imageid))

if large:
    configure_dockerd(uploads=1, downloads=1)
    time.sleep(2)

p = subprocess.run([docker_cmd, 'pull', image_ref], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    for err in p.stderr.split('\n'):
        if err != '':
            print('%s' % (err), file=sys.stderr)
    if large:
        configure_dockerd(uploads=1, downloads=4)

    sys.exit(3)

if large:
    configure_dockerd(uploads=1, downloads=4)
    time.sleep(2)

p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", image_ref], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    for err in p.stderr.split('\n'):
        if err != '':
            print('%s' % (err), file=sys.stderr)
    sys.exit(4)

pull_imageid = p.stdout.split('\n')[0]
print("Id for %s : %s" % (image_ref, pull_imageid))

if force or (current_imageid != pull_imageid):

    # Local upgrade of image
    app = service.split('-')[2]
    p = subprocess.run(["/usr/lib/open-webui-tools/owebui_%s_env_upgrade" % app, pull_imageid],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        for err in p.stderr.split('\n'):
            if err != '':
                print('%s' % (err), file=sys.stderr)
        sys.exit(5)

    # Restart if needed
    p = subprocess.run([systemctl_cmd, 'is-active', '--quiet', service], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 and restart is False:
        print("Service %s is not running. Not restart it" % service)
        sys.exit(0)
    else:
        p = subprocess.run([systemctl_cmd, 'restart', service], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(6)
        else:
            print("Service %s restarted after update" % service)
else:
    print("Nothing to do")
