FROM python:3.12-slim

WORKDIR /library
COPY book_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/library
COPY ./proto ./proto

CMD ["bash", "book_service/start.sh"]