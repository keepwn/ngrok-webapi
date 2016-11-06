# ngrok-webapi
simple webapi wrapper for ngrok


## Introduction
本工具将ngrok的功能封装成RESTful API，方便程序调用

## Requirement
- [docker](https://docs.docker.com/linux/)
- [ngrok 1.x](https://github.com/inconshreveable/ngrok)
  - 不需要自己提供，安装脚本会自动下载并编译

## Run

```bash
git clone git@github.com:keepwn/ngrok-webapi.git
cd ngrok-webapi

# generate ngrok bins
mkdir $(pwd)/ngrok-bin
docker run --rm \
    -e DOMAIN="$DOMIAN" \
    -e TUNNEL_PORT=$TUNNEL_PORT \
    -e HTTP_PORT=$HTTP_PORT \
    -e HTTPS_PORT=$HTTPS_PORT \
    -v $(pwd)/ngrok-bin:/release keepwn/ngrok-self-hosting

# build image: ngrok-webapi
docker build -t ngrok-webapi -f Dockerfile-ngrok-webapi .

# please modify app.conf
# create container and run
docker run -d \
    --name=ngrok-webapi \
    --restart=always \
    -p 5000:5000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ./ngrok-bin:/ngrok-bin
    ngrok-webapi

# enjoy
curl 127.0.0.1:5000/info
```

## Details

ngrok功能的封装是通过docker来实现的:
- 容器的`启动`和`停止`相当于ngrok隧道的`开启`和`关闭`
- 一个容器对应一条ngrok隧道配置，容器之间互不影响