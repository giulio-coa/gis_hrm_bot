FROM python:3-slim

RUN apt update \
  && apt install --assume-yes gcc

WORKDIR /usr/src/app

COPY --chown=root:root ./src ./src
COPY --chown=root:root ./.env ./
COPY --chown=root:root ./requirements.txt ./

RUN pip install --no-cache-dir --no-python-version-warning --requirement requirements.txt

CMD [ "python", "-m", "src.app" ]
