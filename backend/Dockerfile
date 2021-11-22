FROM python:3.8.5
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]