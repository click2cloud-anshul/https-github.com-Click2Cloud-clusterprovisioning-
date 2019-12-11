#Steps for hosting Cluster Provisioning REST APIs on CentOS
**Update the current OS and install some dependencies**
```
yum update -y
yum install -y python-setuptools putty epel-release python-devel gcc gcc-c++ git
```
**Docker installation**
```
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce
systemctl start docker && systemctl enable docker
```
**Httpd service installation and its dependencies**
```
yum install -y httpd mod_wsgi httpd-devel
yum install python-pip -y
pip install --upgrade pip setuptools
pip install mod_wsgi
systemctl start httpd
systemctl enable httpd
systemctl stop firewalld
systemctl disable firewalld
vi /etc/selinux/config
#Set SELINUX = disabled (update this line in the config file)
```
**Clone the repository**
```
cd /var/www/html/
git clone https://github.com/Click2Cloud/clusterprovisioning.git
```
**Provide some environment variables as .env file**
```
#create .env file at location '/var/www/html/clusterprovisioning/clusterProvisioningClient/' which contains

CB_Node_Service=http://XXXXX:XXXXX
DB_Name=XXXXX
DB_User=XXXXX
DB_Password=XXXXX
DB_Host=XXXXX
DB_Port=XXXXX
ENCRYPTION_KEY=XXXXX

#replace XXXXX with its desired values.
```
**Install pip requirements**
```
cd /var/www/html/clusterprovisioning/
pip install -r requirements.txt
cd /var/www/html/
chmod -R 777 clusterprovisioning/
```
**Install S2I dependencies**
```
# Move s2i executable to /usr/bin/local
mv /var/www/html/clusterprovisioning/dependency/binaries/s2i /usr/local/bin/
```
**Change the docker.sock file permissions**
```
# change the permission of docker sock to 777 or else error occurs, Sample:- http://prntscr.com/q60k12
chmod -R 777 /var/run/docker.sock
```
**Configuration file for httpd and Django**
```
mkdir -p /etc/httpd/config.d/
vi /etc/httpd/config.d/django.conf
```
Write the below in the file
```
Alias /static /var/www/html/clusterprovisioning/static
WSGIScriptAlias / /var/www/html/clusterprovisioning/clusterProvisioningClient/wsgi.py
WSGIDaemonProcess clusterprovisioning  python-path=/var/www/html/clusterprovisioning/clusterProvisioningClient:/usr/lib/python2.7/site-packages
WSGIProcessGroup clusterprovisioning
<Directory /var/www/html/clusterprovisioning/clusterProvisioningClient>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
<Directory /var/www/html/clusterprovisioning/static>
Require all granted
</Directory>
```
Update the file '/etc/httpd/conf/httpd.conf' with the content at the end
```
NameVirtualHost *:80
<VirtualHost *:80>
ServerAdmin info@click2cloud.net
ServerName click2cloud.net
ServerAlias http://www.click2cloud.net
DocumentRoot /var/www/html/clusterprovisioning/
ErrorLog /var/log/httpd/clusterprovisioning/error.log
CustomLog /var/log/httpd/clusterprovisioning/access.log combined
WSGIScriptAlias / /var/www/html/clusterprovisioning/clusterProvisioningClient/wsgi.py
#WSGIPythonHome /usr/lib/python2.7
WSGIDaemonProcess clusterprovisioning  python-path=/var/www/html/clusterprovisioning/clusterProvisioningClient:/usr/lib/python2.7/site-packages
WSGIProcessGroup clusterprovisioning
<Directory /var/www/html/clusterprovisioning/clusterProvisioningClient>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
</VirtualHost>
```
Final updates on log files
```
cd /var/log/httpd/
mkdir clusterprovisioning
cd clusterprovisioning
touch error.log
touch access.log
cd /var/log/httpd/
chmod -R 777 clusterprovisioning
```
**Remove unwanted dependencies**
```
yum remove -y gcc gcc-c++ python-devel kernel-devel make postgresql-devel python-pip 
yum clean all   
```