FROM centos:7

## Set build ARGs
ARG REF=ivanchuk-kanchenjunga-1.0.0
ARG BRANCH="master"
ARG COMMIT=""

LABEL name="cluster-provisioner" \
      vendor="Click2Cloud Inc" \
      architecture="x86_64" \
      release=${REF} \
      url="http://click2cloud.com/" \
      maintainer="savasw" \
      branch=${BRANCH}  \
      commit=${COMMIT}

# Copy in your requirements file
COPY requirements.txt /requirements.txt

# OR, if you’re using a directory for your requirements, copy everything (comment out the above and uncomment this if so):
# ADD requirements /requirements

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN set -ex \
    && yum install -y --setopt=tsflags=nodocs --setopt=skip_missing_names_on_install=False epel-release yum-utils unixODBC unixODBC-devel  \
    && BUILD_DEPS=" \
        gcc \
        gcc-c++ \
        python-devel \
        kernel-devel \
        make \
        postgresql-devel \
        python-pip \
    " \
    && yum update -y && yum install -y --setopt=tsflags=nodocs --setopt=skip_missing_names_on_install=False $BUILD_DEPS  

ENV VIRTUAL_ENV=/venv

RUN pip install --upgrade pip \
    && pip install virtualenv \
    && virtualenv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install -U pip \
    && $VIRTUAL_ENV/bin/pip install --no-cache-dir -r /requirements.txt

RUN set -ex \
    && BUILD_DEPS=" \
        gcc \
        gcc-c++ \
        python-devel \
        kernel-devel \
        make \
        postgresql-devel \
        python-pip \
    " \
    && yum remove -y $BUILD_DEPS


# ShiftM dependencies
RUN set -ex \
    && RUNTIME_DEPS=" \
    device-mapper-persistent-data \
    lvm2 \
    git \
    docker-ce-cli \
    "\
    && yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo \
    && yum install -y $RUNTIME_DEPS \
    && yum clean all

# Copy your application code to the container and configuration files
RUN mkdir -p /usr/src/app/cluster-provisioner/
WORKDIR /usr/src/app/cluster-provisioner/
COPY . /usr/src/app/cluster-provisioner/

# make shiftm executable
RUN mv /usr/src/app/cluster-provisioner/dependency/binaries/s2i /usr/local/bin/ \
    && chmod +x /usr/local/bin/s2i

# uWSGI will listen on this port
EXPOSE 8000

# Add any static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=clusterProvisioningClient.settings

# Tell uWSGI where to find your wsgi file (change this):
ENV UWSGI_WSGI_FILE=/usr/src/app/cluster-provisioner/clusterProvisioningClient/wsgi.py

# Base uWSGI configuration (you shouldn't need to change these):
ENV UWSGI_VIRTUALENV=$VIRTUAL_ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Number of uWSGI workers and threads per worker (customize as needed):
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

# to run any sub-process from virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Start uWSGI
CMD ["uwsgi", "--show-config"]