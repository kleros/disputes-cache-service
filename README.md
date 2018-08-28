## Disputes Cache Service

This is a `python3` script that checks for new sessions and adds open disputes to a `dynamodb` table.

#### Quickstart

1) Suggested: Use a `virtualenv`

2) Create `config.py` in the root directory with the following values
```
config = {
    "INFURA_API_KEY": string,
    "KLEROS_CONTRACT_ADDRESS": string,
    "AWS_ACCESS_KEY_ID": string,
    "AWS_SECRET_ACCESS_KEY": string
}
```

3)
```
pip install -r requirements.txt
python3 run.py
```
