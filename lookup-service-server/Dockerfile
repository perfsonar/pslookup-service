FROM python:3

WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/lookup-service-server

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/perfsonar

# Upgrade packages
RUN apt-get update --yes
RUN apt-get upgrade --yes

# Add service user and switch to user
#RUN useradd --create-home apiserviceuser && \
#    chown -R apiserviceuser:apiserviceuser /usr/src/app
#USER apiserviceuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]