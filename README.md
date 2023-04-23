# petition-bot

## Running
Steps:
- create .env file in the project root directory
- create config.py in the bot directory
- docker-compose up -d db
- docker-compose up build -d
- docker-compose up -d api

## API 

### BASE URL
http://localhost:4000/api

### Routes
- /petitions
- /petitions/{id}

## Web
http://localhost:8080