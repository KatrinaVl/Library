FROM python:3.12-slim

WORKDIR /library
# COPY api/requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r alembic/requirements.txt

ENV PYTHONPATH=/library

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY alembic/wait.sh /wait.sh
RUN chmod +x /wait.sh

CMD ["alembic", "upgrade", "head"]

