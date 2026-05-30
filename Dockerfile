FROM python:3.12-slim

WORKDIR /app

COPY src ./src

EXPOSE 6379 8080

CMD ["python", "src/server.py", "--host", "0.0.0.0", "--port", "6379"]
