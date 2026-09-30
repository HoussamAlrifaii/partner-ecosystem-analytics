# deployment scaffold; execute and verify in phase 04.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY partner_analytics ./partner_analytics
COPY sql ./sql
# demo data is generated from the committed seed, not employer exports.
CMD ["sh", "-c", "python -m partner_analytics.generate && python -m partner_analytics.pipeline"]
