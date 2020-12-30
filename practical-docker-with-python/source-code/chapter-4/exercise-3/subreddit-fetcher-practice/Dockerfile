FROM python:3-alpine
COPY * /apps/subredditfetcher/
WORKDIR /apps/subredditfetcher/
RUN ["pip", "install", "-r", "requirements.txt"]
ENV NBT_ACCESS_TOKEN="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"
CMD ["python", "newsbot.py"]