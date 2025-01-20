FROM python:3-slim

ENV TIMEZONE='Europe/Rome'

RUN apt update \
  && apt install --assume-yes gcc tzdata && \
  ln --symbolic --force "/usr/share/zoneinfo/${TIMEZONE}" /etc/localtime && \
  echo "${TIMEZONE}" > /etc/timezone && \
  apt clean all --assume-yes && \
  rm --recursive --force /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY --chown=root:root ./src ./src
COPY --chown=root:root ./.env ./
COPY --chown=root:root ./requirements.txt ./

RUN pip install --no-cache-dir --no-python-version-warning --requirement requirements.txt

CMD [ "python", "-m", "src.app" ]
