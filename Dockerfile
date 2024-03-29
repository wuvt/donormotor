FROM python:3.9.5

RUN apt-get update && apt-get install -y \
            git \
            libcap-dev \
            libjansson-dev \
            libpcre3-dev \
            librsvg2-bin \
            libsasl2-dev \
            libyaml-dev \
            optipng \
            uuid-dev

WORKDIR /usr/src/uwsgi

# prepare uwsgi
RUN wget -O uwsgi-2.0.15.tar.gz https://github.com/unbit/uwsgi/archive/2.0.15.tar.gz && \
        tar --strip-components=1 -axvf uwsgi-2.0.15.tar.gz
COPY uwsgi_profile.ini buildconf/donormotor.ini

# build and install uwsgi
RUN python uwsgiconfig.py --build donormotor && cp uwsgi /usr/local/bin/ && \
        mkdir -p /usr/local/lib/uwsgi/plugins

WORKDIR /usr/src/app

# install python dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# copy application
ADD migrations /usr/src/app/migrations
ADD donormotor /usr/src/app/donormotor
COPY LICENSE README.md uwsgi_docker.ini setup.py /usr/src/app/

VOLUME ["/data/config", "/data/media", "/data/ssl"]

EXPOSE 8443
ENV PYTHONPATH /usr/src/app
ENV FLASK_APP donormotor
ENV APP_CONFIG_PATH /data/config/config.json

RUN python setup.py render_svgs

CMD ["uwsgi", "--ini", "uwsgi_docker.ini"]
