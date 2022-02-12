ARG PYTHON_VERSION="3.9"
FROM python:${PYTHON_VERSION}

WORKDIR /app

COPY requirements-dev.txt run_tests ./

RUN pip install -r requirements-dev.txt

ENTRYPOINT ["./run_tests"]
