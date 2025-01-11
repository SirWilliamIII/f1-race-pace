FROM python:3.9-slim

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]
