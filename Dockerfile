FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CONFIG_FILE=/app/data/config.json \
    DATABASE_FILE=/app/data/journal.db
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py sample_entries.json ./
COPY errors/ ./errors/
COPY models/ ./models/
COPY ai_parts/ ./ai_parts/
COPY logic_parts/ ./logic_parts/
COPY io_parts/ ./io_parts/
COPY data_parts/ ./data_parts/
VOLUME ["/app/data"]
CMD ["python", "main.py"]
