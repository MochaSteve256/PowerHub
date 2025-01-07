# raspbery pi python container
FROM dtcooper/raspberrypi-os:python3.11-bullseye

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]