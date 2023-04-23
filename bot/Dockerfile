# Use a minimal base image (Alpine)
FROM python:3.8-alpine as base

# Install dependencies only (use --no-cache for minimal image)
FROM base as builder
RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY requirements.txt /requirements.txt
RUN pip install --user --no-cache-dir -r /requirements.txt && apk del .build-deps

# Copy installed packages and application code
FROM base
COPY --from=builder /root/.local /root/.local
COPY . /opt/bot

# Set environment variables for minimal image
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "/opt/bot/bot.py"]
