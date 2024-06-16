FROM python:3.11-slim-buster
MAINTAINER Maximilian Thoma
WORKDIR /app
COPY ./app .
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "start_api:app"]