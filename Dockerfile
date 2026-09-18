FROM python:3.12

WORKDIR /meteo_risk

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python"]