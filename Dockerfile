ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a writable home directory for both user and streamlit
ENV HOME=/app
WORKDIR $HOME

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "$HOME" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p $HOME/.streamlit && chown -R appuser:appuser $HOME

COPY . .

USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8000"]
