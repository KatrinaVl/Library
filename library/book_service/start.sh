#!/bin/bash
# start.sh

python3 book_service/database.py &

python3 book_service/book_server.py

# wait