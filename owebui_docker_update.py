#!/usr/bin/python3
import sys
import shutil
import subprocess


if len(sys.argv) != 3:
    print('Usage : %s IMAGE SERVICE' % (sys.argv[0]), file=sys.stderr)
    exit(1)

image = sys.argv[1]
service = sys.argv[2]

docker_cmd = shutil.which('docker')
systemctl_cmd = shutil.which('systemctl')

p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", image], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    current_imageid = None
    print("Image %s not found. Download it" % (image))
else:
    current_imageid = p.stdout.split('\n')[0]
    print("Id for %s : %s" % (image, current_imageid))

p = subprocess.run([docker_cmd, 'pull', image], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    for err in p.stderr.split('\n'):
        if err != '':
            print('%s' % (err), file=sys.stderr)
    sys.exit(3)

p = subprocess.run([docker_cmd, 'inspect', "--format='{{.Id}}", image], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if p.returncode != 0:
    for err in p.stderr.split('\n'):
        if err != '':
            print('%s' % (err), file=sys.stderr)
    sys.exit(4)

pull_imageid = p.stdout.split('\n')[0]
print("Id for %s : %s" % (image, pull_imageid))

if current_imageid != pull_imageid:

    p = subprocess.run([systemctl_cmd, 'is-active', '--quiet', service], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        print("Service %s is not running. Not restart it" % service)
        sys.exit(0)
    else:
        p = subprocess.run([systemctl_cmd, 'restart', service], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            for err in p.stderr.split('\n'):
                if err != '':
                    print('%s' % (err), file=sys.stderr)
            sys.exit(5)
        else:
            print("Service %s restarted after update" % service)
else:
    print("Nothing to do")
