FROM python:3.10-alpine3.16
RUN mkdir /app \
    && addgroup -S appgroup \
    && adduser -h /app -s /sbin/nologin -G appgroup -S -D -H appuser
WORKDIR /app
ADD --chown=appuser:appgroup kv_store.py \
    main.py \
    requirements.txt \
    rest.py \
    tcp.py \
    ./
RUN pip install -r requirements.txt
EXPOSE 8080 8081
USER appuser
CMD ["python", "main.py"]
