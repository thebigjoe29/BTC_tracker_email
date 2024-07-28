# Project Setup
<img src="https://github.com/user-attachments/assets/4d5e69b7-603f-49bc-b807-9db82d3a106e" height="200" width="500" alt="Image description">
<img src="https://github.com/user-attachments/assets/9dc0ecbd-15e0-43f0-bfac-92b76e890367" height="200" width="500" alt="WhatsApp Image 2024-07-29 at 03 50 30_29b5ffbe">
<img src="https://github.com/user-attachments/assets/70a34e95-57f0-4060-bf25-6007628651d9" height="300" width="500" alt="WhatsApp Image 2024-07-29 at 03 37 44_5893e671">
<img src="https://github.com/user-attachments/assets/a60fad7c-9a59-4e64-be47-88061354e4a2" height="300" width="500" alt="WhatsApp Image 2024-07-29 at 03 39 52_53189760">





## Prerequisites

- Python 3.x
- pip
- RabbitMQ (message broker)
- Redis (caching tool)
- Celery (API task queuer)

## Steps

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```
### 2. Install requirements
```bash
pip install -r requirements.txt
```
### 3. Ensure servers are up and running
```bash
redis-server
rabbitmq-server
mysql server
```
### 4. Start the celery worker
```bash
celery -A myproject worker --pool=solo -l info
```
### 5. Start the Django server and migrations

```bash
python manage.py migrate && python manage.py runserver
```
## API Endpoints
1. <b> LOGIN THE USER </b><br>
   method: POST<br>
   body:
   {
      "email": "youremail@example.com",
      "password": "yourpassword"
   }
    
```bash
http://127.0.0.1:8000/api/login/
```
2. <b> REGISTER THE USER </b><br>
   method: POST<br>
   body:
    {
      "email": "youremail@example.com",
      "password": "yourpassword"
   }
```bash
http://127.0.0.1:8000/api/register/
```
3. <b> CREATE AN ALERT </b><br>
   method: POST <br>
   body: {
      "price": 51000
   }
```bash
http://127.0.0.1:8000/api/alerts/create
```
4. <b> DELETE ALERT WITH GIVEN ID </b><br>
   method: POST
```bash
http://127.0.0.1:8000/api/delete/<replace_with_alert_id>
```
5.<b> FETCH ALL ALERTS </b><br>
   method: GET
```bash
http://127.0.0.1:8000/api/alerts/
```
6. <b> FETCH ALERTS FILTERED BY STATUS </b><br>
   method: GET
```bash
http://127.0.0.1:8000/api/alerts/<replace_with_alert_status>
```
## Alert logic and User auth
### Current price of BTC (USD) is fetched from Binance's live price API endpoint
```bash
https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT
```
1. A user registers themselves using the<b> /register</b> API using a valid email and password.
2. The user logs in using the <b> /login </b> the same credentials.
3. On successul login, a JWT (JSON Web Token) is returned, with user_email embedded in it.
4. All subsequent APIs will require Bearer authentication using these tokens. (30 min validity).
5. The user can create an alert with his desired price in the price parameter of the request body.
6. A celery worker is instantiated as soon as the request is received by the server that checks for changes every 10s.
7. If the current BTC price is greater than or equal to the request_price, the Email job will be triggered and Celery will send an email to the user immediately.
8. If the condition fails, Celery will infinitely keep a watch on the BTC price and send the Email as soon as the condition is met.
9. Only alerts with status="created" are kept in task queues and rest are only stored in the MySql database.
10. Once an alert has been triggered, its status is changed to "triggered" and it is dequeued.

## Caching, Pagination and GET APIs
1. Using Django-Redis, all GET alert responses will be cached locally for a fixed period of time.
2. This will increase retrieval speed and avoid unnecessary API calls.
3. However Celery will continue fetching current BTC prices even if cached data is available to ensure data consistency.
4. <b>Using status as a parameter, the user can fetch alerts filtered by the status, eg. created, triggered, deleted etc.<b>
5. All GET responses are <b> paginated<b> for easy access with count, next page url and number of entries per page provided with each response.

## Models
### 1. User model:
id(int)<br>email(String)<br>password (String)
### 2. Alert model:
id(int)<br>email(String)<br>status(String)<br>price (int)


