import json
from web3 import Web3, HTTPProvider

with open('data/data.json') as data_json:
    DATA = json.load(data_json)

# open the secrets
with open('data/secret.json') as secret_json:
    secret = json.load(secret_json)

PROVIDER = secret['provider']
w3 = Web3(HTTPProvider(PROVIDER))

blockNum = 12688544-1  # first sell on rugpull https://etherscan.io/tx/0x0ba4dff34be3b9f9f4745b6e783c108e98172dfa6f5dccd9f833d3521348d9fd


def createGeysers(g_addresses):
    with open('data/geysers.json') as g_json:
        geyserDATA = json.load(g_json)
    geysers = []
    for g in g_addresses:
        g_address = Web3.toChecksumAddress(g)
        geyser = w3.eth.contract(abi=geyserDATA['abi'], address=g_address)
        geysers.append(geyser)
    return geysers


def getStaked(address, geysers):
    # get the staked balances
    balance = 0
    for geyser in geysers:
        balance += geyser.functions.balanceOf(
            address).call(block_identifier=blockNum)
    return balance


def getBalances(c_address, g_addresses, addresses):
    BALANCES = {}
    contract = w3.eth.contract(abi=DATA['abi'], address=c_address)
    geysers = createGeysers(g_addresses)
    # get plain balance
    counter = 0
    for address in addresses:
        balance = 0
        balance = contract.functions.balanceOf(
            address).call(block_identifier=blockNum)
        balance += getStaked(address, geysers)
        if balance > 0:
            BALANCES[address] = balance
        counter += 1
        print(counter, end="\r", flush=True)
    return BALANCES


def GetSnapshot(key, c_address, g_addresses):
    with open(f'results/addresses_{key}.json') as addresses_json:
        addresses = json.load(addresses_json)
    BALANCES = getBalances(c_address, g_addresses, addresses)

    # delete blacklisted addresses: geysers, deployers, devs.
    with open('data/blacklist.json') as b_json:
        blacklist = json.load(b_json)
    for address in blacklist:
        a = Web3.toChecksumAddress(address)
        BALANCES.pop(a, None)

    print(f"Addresses w balance on Snapshot: {len(BALANCES)}")
    print(f"Total of {sum(BALANCES.values())} LP tokens.")
    with open(f'results/BALANCES_{key}.json', 'w') as out:
        json.dump(BALANCES, out)
