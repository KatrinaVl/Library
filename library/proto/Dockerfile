FROM python:3.12-slim

WORKDIR /library

COPY proto/ proto/
COPY proto/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/book_service.proto"

COPY . .


