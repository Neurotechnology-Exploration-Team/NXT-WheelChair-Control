FROM python:latest

COPY src /

CMD ["ls", "/src"]
#CMD ["python3", "/src/main.py"]
