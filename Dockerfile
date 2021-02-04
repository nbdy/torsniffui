FROM python:slim

RUN apt-get update ; apt-get upgrade -y ; apt-get install git python3 python3-dev python3-pip
RUN pip3 install git+https://github.com/nbdy/torsniffui
RUN mkdir /torsniff_data

VOLUME "/torsniff_data"
EXPOSE 1668/tcp

CMD ["torsniffui"]