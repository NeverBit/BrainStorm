FROM python:alpine3.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD python -m python -m BrainStorm.server run-server rabbitmq://rabbit_host:5672/ -p 8000