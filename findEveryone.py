import json
from web3 import Web3, HTTPProvider

# open the secrets
with open('data/secret.json') as secret_json:
    secret = json.load(secret_json)

PROVIDER = secret['provider']
w3 = Web3(HTTPProvider(PROVIDER))


def getEvents(address):
    event_sig_hash = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"  # transfer
    filterer = {
        'fromBlock': 11779879,  # block of creation
        'address': address,
        'topics': [event_sig_hash],
    }
    filter = w3.eth.filter(filterer)
    event_logs = filter.get_all_entries()
    # we have all the events for transfers, now lets get all of the addresses that had ever held V2
    return event_logs


# input: 0x000...00ADDRESS
def normalize(address):
    # OUTPUT: 0xADDRESS
    return Web3.toChecksumAddress("0x"+address[26:])


def getAdresses(event_logs):
    allAddresses = []
    for event in event_logs:
        for i in range(1, 2):
            a = normalize(event.topics[i].hex())
            allAddresses.append(a)
    allAddresses = list(set(allAddresses))  # get unique addresses
    print(f"Unique address count : {len(allAddresses)}")
    return allAddresses


def GetEveryone(key, address):
    event_logs = getEvents(address)
    addresses = getAdresses(event_logs)
    with open(f'results/addresses_{key}.json', 'w') as out:
        json.dump(addresses, out)
