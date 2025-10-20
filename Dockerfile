FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn
EXPOSE 8000
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]