#!/usr/bin/python3
import sys
import shutil
import subprocess


if len(sys.argv) > 6 or len(sys.argv) < 3:
    print('Usage : %s IMAGE SERVICE [IMAGE_SRC] [--force] [--restart]' % (sys.argv[0]), file=sys.stderr)
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

p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", image_ref], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    current_imageid = None
    print("Image %s not found. Download it" % (image_ref))
else:
    current_imageid = p.stdout.split('\n')[0]
    print("Id for %s : %s" % (image_ref, current_imageid))

p = subprocess.run([docker_cmd, 'pull', image_ref], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    for err in p.stderr.split('\n'):
        if err != '':
            print('%s' % (err), file=sys.stderr)
    sys.exit(3)

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
