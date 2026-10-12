# kgi-sparql-queries container image

FROM python:3.12-slim

# install the dependencies in their own layer for faster rebuilds
COPY pyproject.toml /build/
RUN python -c "import sys, tomllib; \
        project = tomllib.load(sys.stdin.buffer)['project']; \
        print('\n'.join(project['dependencies']))" \
        < /build/pyproject.toml > /build/requirements.txt \
    && pip install --no-cache-dir --requirement /build/requirements.txt

# install the package itself; the build files are not needed afterwards
COPY README.md LICENSE /build/
COPY kgi_example_queries /build/kgi_example_queries
RUN pip install --no-cache-dir --no-deps /build && rm -rf /build

# unprivileged user
RUN useradd --create-home kgi
USER kgi

# the repository is mounted here: data/sources.yaml is read, query-sets/ is written
WORKDIR /work

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["kgi-queries"]
CMD ["harvest"]
