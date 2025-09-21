# tJoy Backend

## Start up command
```bash
uvicorn --host 0.0.0.0 --port 8080 --env-file .env api:app
```

## Env config
```bash
FORWARDED_ALLOW_IPS=127.0.0.1
PUBLIC_KEY=ecc-pub.pem
PRIVATE_KEY=ecc-key.pem
DB_URL=postgresql+asyncpg://user:password@127.0.0.1/postgres
```

## Generate ecc key
```bash
openssl ecparam -genkey -name prime256v1 -out ecc-key.pem
openssl ec -in ecc-key.pem -pubout -out ecc-pub.pem
openssl pkcs8 -topk8 -inform PEM -outform DER -in ecc-key.pem -out ecc-key.der -nocrypt
```
