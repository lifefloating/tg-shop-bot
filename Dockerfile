FROM python:3.10-alpine AS dependencies
RUN apk update && \
    apk add --no-cache \
        --repository https://dl-cdn.alpinelinux.org/alpine/v3.17/main \
        --repository https://dl-cdn.alpinelinux.org/alpine/v3.17/community \
        build-base python3-dev py3-pip

# gevent dependency 
RUN apt-get install musl-tools

WORKDIR /usr/src/TGgreed
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

#############################################################################

FROM python:3.10-slim AS final

COPY --from=dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

WORKDIR /usr/src/TGgreed
COPY . /usr/src/TGgreed

RUN mkdir -p /var/lib/TGgreed/

ENTRYPOINT ["python", "-OO"]
CMD ["core.py"]

ENV PYTHONUNBUFFERED=1
#ENV CONFIG_PATH="/etc/TGgreed/config.toml"
ENV DB_ENGINE="sqlite:////var/lib/TGgreed/database.sqlite"

LABEL org.opencontainers.image.title="TGgreed"
LABEL org.opencontainers.image.description="A customizable, multilanguage Telegram shop bot"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.authors="fuyou-jacky"