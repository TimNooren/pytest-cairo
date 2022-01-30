ARG PYTHON_VERSION="3.9"
FROM python:${PYTHON_VERSION}

WORKDIR /app

COPY requirements-dev.txt .

RUN pip install -r requirements-dev.txt

ENTRYPOINT ["pytest", "--override-ini", "cache_dir=.pytest_cache/${PYTHON_VERSION}"]