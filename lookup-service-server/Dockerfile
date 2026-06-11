FROM python:3

WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/lookup-service-server

RUN pip install --no-cache-dir -r requirements.txt

ENV V1_LOG_DIR=/var/log/perfsonar

RUN mkdir -p $V1_LOG_DIR

# Upgrade packages
RUN apt-get update --yes
RUN apt-get upgrade --yes

# Add service user and switch to user
RUN useradd --create-home apiserviceuser && \
    chown -R apiserviceuser:apiserviceuser /usr/src/app && \
    chown apiserviceuser:apiserviceuser $V1_LOG_DIR
USER apiserviceuser

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]