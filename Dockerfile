FROM python:3.12.0b4-alpine3.18

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add --no-cache musl-dev postgresql-dev python3-dev libffi-dev \
    && pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install -r  requirements.txt

COPY ./ ./

RUN apk add --no-cache file exiftool

RUN python manage.py makemigrations
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
