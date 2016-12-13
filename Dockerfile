FROM python:3-alpine
MAINTAINER keepwn <keepwn@gmail.com>

RUN apk update && \
    apk add git && \
    git clone https://github.com/keepwn/ngrok-webapi.git /ngrok-webapi && \
    apk del --purge git && \
    rm -rf /var/cache/apk/*

WORKDIR /ngrok-webapi
RUN pip3 install -r requirements.txt

ENV SERVER_ADDR ''
ENV TRUST_HOST_ROOT_CERTS ''
ENV RUNTIME_DIR ''
ENV RUNTIME_DIR_IN_CONTAINER ''

EXPOSE 5000

CMD ["sh", "run.sh"]