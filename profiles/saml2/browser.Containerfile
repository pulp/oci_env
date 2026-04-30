FROM debian:latest

RUN \
  apt-get update && \
  apt-get install extrepo -y && \
  extrepo enable librewolf && \
  extrepo update librewolf && \
  apt-get update && \
  apt-get install librewolf -y && \
  apt-get clean

COPY librewolf.overrides.cfg /root/.librewolf/librewolf.overrides.cfg

CMD librewolf
