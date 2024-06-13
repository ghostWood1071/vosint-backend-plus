FROM python:3.10-bullseye

WORKDIR /usr/app


COPY requirements.txt .
RUN pip install -r requirements.txt 

COPY . .

RUN mkdir secrets

RUN ssh-keygen -t rsa -b 4096 -m PEM -E SHA512 -f secrets/PRIVATE_KEY

RUN openssl rsa -in secrets/PRIVATE_KEY -pubout -outform PEM -out secrets/PUBLIC_KEY

EXPOSE 6102

CMD [ "python","main.py"]

