FROM ghcr.io/astral-sh/uv:0.13.6 AS uv

# Shared base: the locked runtime dependencies and the king_county package.
FROM python:3.13.17-slim-bookworm AS train

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY --from=uv /uv /uvx /bin/
# Install dependencies before copying the code, so code changes reuse this layer.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

COPY data ./data
COPY king_county ./king_county

# Run as an unprivileged user instead of root. It owns /app so the trained
# model can be written to /app/model.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Train, print the test scores, and save the model to /app/model/model.bin.
CMD ["python", "-m", "king_county.model"]


# Test image: adds the dev dependencies (pytest) and the tests.
FROM train AS test

USER root
RUN uv sync --locked --no-install-project
COPY tests ./tests
USER appuser

CMD ["python", "-m", "pytest", "-q"]
