FROM python

WORKDIR /usr/app/
COPY /app /usr/app/

RUN pip install -r requirements.txt
CMD python app.py

