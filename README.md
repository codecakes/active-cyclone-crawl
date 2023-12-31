# What?

A micro service which obtains information on active tropical cyclones. Uses python3.6 and best practices.

Data is sourced in and constantly crawled from source for the latest information in database.

## Stack & Implementation details
- Postgres database 
- Redis queue
- A Cyclone scraper as a celery task to obtain live cyclone information from http://rammb.cira.colostate.edu/products/tc_realtime/index.asp
- Crawled information stored in postgres database.
- A celery scheduler to schedule the cyclone scraper to run per schedule using queue with results stored in redis.
- A simple REST api to query the cyclone information.
- Dockerfile and the corresponding docker-compose.yml file for orchestrating the whole process including setting up the local database and the queue.

## Steps to run it:

1. Unzip it. Make sure docker engine is up and running;
2. Run like `docker-compose up --build -d` and you should be able to see containers running on this image; (On Mac its easy to check using docker-for-desktop) Then,
3. If you prefer open-api json test it like: http://localhost:8000/cyclones/?format=openapi-json | 
If you prefer regular swagger schema look: http://localhost:8000/cyclones/
4. Try it out in the following ways:

    If you want to look at active cyclone within last 1 Hr try: http://localhost:8000/cyclones/?H=1&format=openapi-json 

     If you want to look at active cyclones within the last 3 Hrs 2 mins, for e.g., try: http://localhost:8000/cyclones/?H=3&M=2
     
     Similarly, time parameters are supported in standard timestamp format.
5. To test cd to /web and do `TEST_ENV=1 python3 manage.py test`


## Env settings for local docker run

A local `.env` file is needed to run the setup like this. Use the desired values for production and never include this file in version or during file transfers:

```bash
SECRET_KEY="1^1$)eoun(k_6@enm+d20#4=&9_^92kh)r^_e\!d*-&9=qjj7%"
#TEST_ENV=1
DEBUG_ENV=1
DB_NAME=postgres
DB_USER=postgres
DB_USER_PWD=postgres
DB_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DJANGO_SETTINGS_MODULE="backend.settings"
DJANGO_ALLOWED_HOST="localhost"
DB_HOST="postgres"
PROJECT_NAME="backend"
```