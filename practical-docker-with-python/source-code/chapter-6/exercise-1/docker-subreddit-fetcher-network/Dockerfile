FROM python:3-alpine
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
COPY * /apps/subredditfetcher/
WORKDIR /apps/subredditfetcher/

VOLUME [ "/apps/subredditfetcher" ]
RUN ["pip", "install", "-r", "requirements.txt"]

ENV NBT_ACCESS_TOKEN="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"

CMD ["python", "newsbot.py"]
