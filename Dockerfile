FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 FLASK_APP=app.py
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/entrypoint.sh \
 && useradd --create-home --uid 1000 appuser \
 && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/users',timeout=2).status==200 else 1)"
ENTRYPOINT ["/app/entrypoint.sh"]
