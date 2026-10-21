FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY src ./src
COPY api ./api
COPY cli ./cli
COPY scripts ./scripts
RUN pip install --no-cache-dir -r requirements.txt
ARG WITH_VLM=false
RUN if [ "$WITH_VLM" = "true" ]; then pip install --no-cache-dir '.[local-vlm]'; fi
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
