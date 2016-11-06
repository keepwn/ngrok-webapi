FROM python:3-alpine
MAINTAINER keepwn <keepwn@gmail.com>

RUN apk update && \
    apk add git && \
    git clone https://github.com/keepwn/ngrok-webapi.git /code && \
    apk del --purge git && \
    rm -rf /var/cache/apk/*

WORKDIR /code
RUN pip3 install -r requirements.txt

VOLUME ['/release']
EXPOSE 5000

CMD ["sh", "run.sh"]