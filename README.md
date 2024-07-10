
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

Install dependencies (recommended : create a virtual environment)

```bash
  pip install -r requirements.txt
```

Create a .env file (your credentials)

```bash
  Add DATABASE_URL=postgresql://pguser:pgpassword@pghost/pgdatabase
```

Start the server

```bash
  flask run
```


## Deployed Link

```bash
  https://identity-reconciliation-iota.vercel.app/identify

  Method : POST
```