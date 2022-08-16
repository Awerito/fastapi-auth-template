FROM python:3.10.4-alpine AS compile-image

RUN apk update
RUN apk add --no-cache gcc

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10.4-alpine AS build-image

COPY --from=compile-image /root/.local /root/.local

WORKDIR /app

COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD [ "python", "main.py" ]
