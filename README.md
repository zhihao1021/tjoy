# TCard Backend

## Generate ecc key
```bash
openssl ecparam -genkey -name prime256v1 -out ecc-key.pem
openssl ec -in ecc-key.pem -pubout -out ecc-pub.pem
openssl pkcs8 -topk8 -inform PEM -outform DER -in ecc-key.pem -out ecc-key.der -nocrypt
```