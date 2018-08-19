FROM python:3.6-alpine
ADD . /source
WORKDIR /source
RUN pip install -r requirements.txt
CMD ["./start_flask_app.sh" ]