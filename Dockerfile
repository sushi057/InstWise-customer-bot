FROM python:3.12.3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt 

COPY . /code

CMD ["uvicorn", "main:app" , "--reload"] 
