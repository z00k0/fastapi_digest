FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

EXPOSE 5050

COPY . /app

ENTRYPOINT ["python"]
CMD ["main.py"]