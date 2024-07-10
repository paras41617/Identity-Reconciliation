
# Identity Reconciliation

A web service which provides a way to identify and keep track of a customer's identity across multiple purchases.

It will receive HTTP POST requests with
JSON body.
The web service should return an HTTP 200 response with a JSON payload containing the consolidated contact.


Request Format

```bash
  {
  "email":"mcfly@hillvalley.edu",
  "phoneNumber":"123456"
  }
```

Response Format

```bash
  {
    "contact":{
    "primaryContatctId": 1,
    "emails": ["lorraine@hillvalley.edu","mcfly@hillvalley.edu"]
    "phoneNumbers": ["123456"]
    "secondaryContactIds": [23]
    }
  }
```
## Tech Stack

**Server:** Python, Django

**Database:** PostgreSQL


## Run Locally

Clone the project

```bash
  git clone https://github.com/paras41617/Identity-Reconciliation
```

Go to the project directory

```bash
  cd Identity-Reconciliation-master
```

Create a .env file (your credentials)

```bash
  Add DATABASE_URL=postgresql://pguser:pgpassword@pghost/pgdatabase
```

#### Via Localhost 

Install dependencies (recommended : create a virtual environment)

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  flask run
```

#### Using Docker

Create the Docker Image

```bash
  docker build -t paras41617-identity-reconciliation .
```

Run the Container (ensure that 5000 port is not being used by any other service)

```bash
  docker run -p 5000:5000 paras41617-identity-reconciliation
```


## Deployed Link

```bash
  https://identity-reconciliation-iota.vercel.app/identify

  Method : POST
```