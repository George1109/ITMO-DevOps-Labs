FROM debian:stable-slim
RUN apt-get update && apt-get install -y cowsay fortune
COPY ep.sh /

ENTRYPOINT ["/ep.sh"]