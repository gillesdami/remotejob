FROM python:3.6

RUN pip install Pyro4 dill
WORKDIR /var/www

COPY slave.py /var/www/main.py
EXPOSE 8000

ENTRYPOINT [ "python", "main.py" ]