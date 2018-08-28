import json
import time
import os
import boto3

from config import config

os.environ['INFURA_API_KEY'] = config["INFURA_API_KEY"]
from web3.auto.infura import w3


if __name__ == "__main__":
    assert(w3.isConnected())

    run = True

    # aws
    aws_client = boto3.client(
        'dynamodb',
        aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
        region_name='us-east-2'
    )

    # contract
    kleros_json = open(file='contracts/Kleros.json')
    abi = json.loads(kleros_json.read())['abi']
    kleros_contract = w3.eth.contract(
        address=w3.toChecksumAddress(config['KLEROS_CONTRACT_ADDRESS']),
        abi=abi
    )

    # disputes cache
    closed_disputes = {}
    existing_session_data = {}

    def session_exists(session):
        if existing_session_data.get(session):
            return True
        session_data = aws_client.get_item(
            TableName='disputes',
            Key={
                'session': {"N": str(session)}
            }
        )
        if (session_data.get("Item")):
            existing_session_data[session] = True
            return True
        else:
            return False

    def update_dyanmo_db(session, open_disputes):
        if not session_exists(session):
            aws_client.put_item(
                TableName='disputes',
                Item={
                    'session': {"N": str(session)},
                    'open_disputes': {"NS": [str(d) for d in open_disputes]}
                }
            )

    while run:
        session = kleros_contract.call().session()
        period = kleros_contract.call().period()
        # we can wait if we aren't in voting period of new session
        if session_exists(session) or period != 2:
            time.sleep(10)
            continue

        # get new open disputes
        open_disputes = []
        check_disputes = True
        dispute_id = 0
        while check_disputes:
            if closed_disputes.get(dispute_id):
                continue
            try:
                dispute = kleros_contract.call().disputes(dispute_id)
                if dispute[1] + dispute[2] == session:
                    open_disputes.append(dispute_id)
                else:
                    closed_disputes[dispute_id] = True
            except:
                check_disputes = False
            dispute_id += 1

        update_dyanmo_db(session, open_disputes)
        print("Added %d disputes for session %d" % (len(open_disputes), session))
