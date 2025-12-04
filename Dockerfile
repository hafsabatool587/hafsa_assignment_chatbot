FROM python:3.10-slim
WORKDIR /app

# Copy requirements & install
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app, utils & frontend
COPY app.py /app/
COPY .env /app/.env
COPY utills.py /app/
COPY frontend/ /app/frontend/
RUN mkdir -p pdf_files

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
