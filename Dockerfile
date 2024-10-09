FROM python:3.10-alpine
WORKDIR /vbotaio3
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .
COPY . .
ENV TZ Asia/Almaty
CMD ["python3", "-u", "run_bot.py"]