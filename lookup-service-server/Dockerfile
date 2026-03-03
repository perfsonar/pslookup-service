FROM python:3

WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/lookup-service-server

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update

RUN apt-get upgrade

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]