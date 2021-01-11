FROM python:3-alpine

RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
COPY * /apps/subredditfetcher/
WORKDIR /apps/subredditfetcher/

VOLUME [ "/apps/subredditfetcher" ]
RUN ["pip", "install", "-r", "requirements.txt"]
# RUN ["python", "one_time.py"]

ENV NBT_ACCESS_TOKEN="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"

CMD ["python", "one_time.py"]
CMD ["python", "newsbot.py"]
