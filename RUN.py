from eth_utils import address
from web3 import Web3, HTTPProvider
import json
from buildData import BuildData
from getSnapshot import GetSnapshot
from findEveryone import GetEveryone

# open the secrets
with open('data/secret.json') as secret_json:
    secret = json.load(secret_json)

PROVIDER = secret['provider']
w3 = Web3(HTTPProvider(PROVIDER))
BLOCK = 12688512-1  # first sell on rugpull https://etherscan.io/tx/0x6c13433b0c8539ab2fdf892eb4457d0c045db22755fa9c053f906c257de89a41

addresses = {
    "ETH_UNI": Web3.toChecksumAddress(
        "0x3d07f6e1627da96b8836190de64c1aed70e3fc55"),
    "vETH2_UNI": Web3.toChecksumAddress(
        "0xc794746df95c4b7043e8d6b521cfecab1b14c6ce")
}
geysers = {
    "ETH_UNI": [Web3.toChecksumAddress("0x77d03ecC4d6a15C320dd3849973aA3a599cBB07F"),
                Web3.toChecksumAddress("0x64A1DB33f68695df773924682D2EFb1161B329e8")],
    "vETH2_UNI": [Web3.toChecksumAddress("0x53dc9D5deB3B7f5cD9A3E4D19A2beCda559D57Aa")]
}

returned = {
    "vETH2_UNI": 101.14731789866243604*1e18,
    "ETH_UNI": 26.1*1e18
}
if __name__ == "__main__":
    lastBlock = w3.eth.get_block('latest')  # get current balances
    lastBlock = lastBlock.number
    print(f"snapshot Block:{BLOCK},last Block:{lastBlock}")
    for key, c_address in addresses.items():
        print(f"\nLP token : {key}")
        GetEveryone(key, c_address)
        GetSnapshot(key, c_address, geysers[key], BLOCK, lastBlock)
        BuildData(key, c_address, returned[key], BLOCK, lastBlock)
    print("DONE")
