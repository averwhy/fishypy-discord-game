FROM python:3.12
WORKDIR /bot

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY fishy.py .
COPY avatar.png .
COPY cogs ./cogs

CMD ["python", "fishy.py"]