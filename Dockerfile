FROM python:3.6-alpine

COPY requirements.txt /req/
RUN pip install -r /req/requirements.txt

COPY . /code
WORKDIR /code

CMD ["./serve_flask_app.sh" ]