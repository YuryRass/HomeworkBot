FROM docker:24.0.6

ENV APP_NAME dind
ENV APP_INSTALL_PATH /opt/${APP_NAME}

WORKDIR ${APP_INSTALL_PATH}

COPY docker_scripts .
COPY . .

RUN apk add --no-cache iptables bash \
	python3 py3-pip py3-virtualenv py3-distutils-extra

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "./start.sh" ]
