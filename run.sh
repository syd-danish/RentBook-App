docker build -t my-flask-app .
docker run -d -p 8080:80 --name flask-container my-flask-app
docker-compose up -d
