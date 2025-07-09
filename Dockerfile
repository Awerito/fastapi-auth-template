FROM python:3.11-alpine AS compiler

WORKDIR /app/

RUN apk update
RUN apk add --no-cache gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt
RUN pip install -Ur requirements.txt

FROM python:3.11-alpine

WORKDIR /app/ 
COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app/
EXPOSE 8000
CMD [ "fastapi", "run", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
