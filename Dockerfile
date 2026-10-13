FROM python:3.12-slim

# print output straight away (needed for the interactive prompts)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CONFIG_FILE=/app/data/config.json

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
# main.py imports "ai_manager", but the file is named ai-manager.py
RUN if [ -f ai-manager.py ]; then mv ai-manager.py ai_manager.py; fi

# config.json lives here; mount a host folder over it so it persists
VOLUME ["/app/data"]

CMD ["python", "main.py"]
