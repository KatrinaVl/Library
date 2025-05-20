FROM python:3.12-slim

WORKDIR /library
COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/library
COPY ./proto ./proto

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY api/wait.sh /wait.sh
RUN chmod +x /wait.sh


CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8090", "--reload"]
