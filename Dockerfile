FROM python:3.10.4-alpine AS compiler

WORKDIR /app/

RUN apk update
RUN apk add --no-cache gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt
RUN pip install -Ur requirements.txt

FROM python:3.10.4-alpine AS runner

WORKDIR /app/ 
COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app/
EXPOSE 8000
CMD [ "python", "main.py" ]
