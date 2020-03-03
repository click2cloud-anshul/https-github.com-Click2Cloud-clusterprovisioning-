import os
import subprocess

# Note always run this file in Administrator user mode in Windows and with root user in Linux

# rootdir for location of project code
rootdir = '<>'
compiled_dir = []

for subdir, dirs, files in os.walk(rootdir):
    if (subdir != rootdir) and ('dist' not in subdir) and ('.git' not in subdir) and ('.idea' not in subdir):
        print(subdir)
        data = {
            "source_dir": subdir,
            "dest_dir": str(subdir).replace('clusterProvisioningClient', 'clusterProvisioningClient-compiled')
        }
        compiled_dir.append(data)

os.mkdir(rootdir.replace('clusterProvisioningClient', 'clusterProvisioningClient-compiled'))
for dir in compiled_dir:
    print('pyarmor obfuscate ' + '"' + dir['source_dir'] + '"')
    os.mkdir(dir['dest_dir'])
    p1 = subprocess.Popen('pyarmor obfuscate ' + '"' + dir['source_dir'] + '"', cwd=dir['source_dir'])
    p1.wait()

for dir in compiled_dir:
    print('xcopy ' + os.path.join(dir['source_dir'], 'dist') + ' ' + dir['dest_dir'] + ' /o /x /e /h /k')
    os.system('xcopy ' + os.path.join(dir['source_dir'], 'dist') + ' ' + dir['dest_dir'] + ' /o /x /e /h /k')

# cmd = 'pyarmor obfuscate "' + os.path.join(rootdir, 'manage.py') +'"'
p2 = subprocess.Popen('pyarmor obfuscate ' + '"' + os.path.join(rootdir, 'manage.py') + '"', cwd=rootdir)
p2.wait()
cmd2 = 'xcopy ' + os.path.join(rootdir, 'dist') + ' ' + rootdir.replace('clusterProvisioningClient',
                                                                        'clusterProvisioningClient-compiled') + ' /o /x /e /h /k'
cmd3 = 'copy ' + os.path.join(rootdir, 'clusterProvisioningClient') + '\\*.env ' + \
       os.path.join(rootdir.replace('clusterProvisioningClient', 'clusterProvisioningClient-compiled'),
                    'clusterProvisioningClient')

# os.system(cmd)
# print(cmd)
print("\n")
os.system(cmd2)
print(cmd2)
print(cmd3)
os.system(cmd3)
