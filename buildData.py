import json
from web3 import Web3, HTTPProvider
import pandas as pd
import openpyxl

with open('data/data.json') as data_json:
    DATA = json.load(data_json)
# open the secrets

with open('data/secret.json') as secret_json:
    secret = json.load(secret_json)

PROVIDER = secret['provider']
w3 = Web3(HTTPProvider(PROVIDER))

blockNum = 12688512-1  # first sell on rugpull https://etherscan.io/tx/0x6c13433b0c8539ab2fdf892eb4457d0c045db22755fa9c053f906c257de89a41

pd.options.display.float_format = '{:.18f}'.format


def calculateWithdrawals(event):
    if event['removed'] == False:
        hash = event["transactionHash"]
        tx = w3.eth.getTransaction(hash)
        sender = tx['from']
        data = event['data']
        amount = int(data[66:], 16)
        return hash.hex(), sender, amount
    return None


def getWithdrawals(c_address, BLOCK, lastBlock):
    TOTAL = 0
    event_sig_hash = "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496"  # burn
    filterer = {
        'fromBlock': BLOCK,  # after rug
        'toBlock': lastBlock,
        'address': c_address,
        'topics': [event_sig_hash],
    }
    filter = w3.eth.filter(filterer)
    event_logs = filter.get_all_entries()
    # we have all the events for transfers, now lets get all of the addresses that had ever held V2
    withdrawalList = set()
    for e in event_logs:
        w = calculateWithdrawals(e)
        TOTAL += w[2]
        withdrawalList.add(w)
    print(f"total withdrawals: {TOTAL/1E18}")
    return withdrawalList


# def getCurrentReserve(c_address):
#     contract = w3.eth.contract(abi=DATA['abi'], address=c_address)
#     reserves = contract.functions.getReserves().call()
#     return reserves[1]


def buildReport(BALANCES, WITHDRAWALS, returned, lastBALANCES, BLOCK):
    etherscanPre = "https://etherscan.io/tx/"
    BlDf = pd.DataFrame(BALANCES, index=[f"bal_on_{BLOCK}"])
    BlDf = BlDf.transpose()
    BlDf['withdrawn'] = 0.0
    BlDf['burn_TXs'] = ""
    for w in WITHDRAWALS:
        if w[1] in BlDf.index:
            BlDf.loc[w[1], "withdrawn"] += w[2]
            if(BlDf.loc[w[1], "burn_TXs"] == ""):
                BlDf.loc[w[1], "burn_TXs"] = (etherscanPre + w[0])
            else:
                BlDf.loc[w[1], "burn_TXs"] = (
                    BlDf.loc[w[1], "burn_TXs"]+" \ "+etherscanPre+w[0])
    BlDf['current'] = 0.0
    for b in lastBALANCES:
        BlDf.loc[b, "current"] += lastBALANCES[b]
    BlDf['loss'] = BlDf[f"bal_on_{BLOCK}"] - BlDf["withdrawn"]
    BlDf['loss'] = BlDf['loss'] - BlDf['current']
    BlDf['returned'] = (BlDf['loss'] / BlDf['loss'].sum())*returned
    return BlDf


def getPrice(c_address, BLOCK):
    contract = w3.eth.contract(abi=DATA['abi'], address=c_address)
    EthPerToken = 0
    reserves = contract.functions.getReserves().call(block_identifier=BLOCK)
    totalSupply = contract.functions.totalSupply().call(block_identifier=BLOCK)
    # not a problem since both tokens are second in uni pools
    EthReserve = reserves[1]
    EthPerToken = EthReserve/totalSupply
    return EthPerToken


def convertBalances(price, BALANCES):
    BALANCES.update((x, y*price) for x, y in BALANCES.items())
    # so here we got the balances (just pre-rug block)
    # now we will get the withdrawals and save them with legit numbers
    # damage will be = Balance-withdrawals for an address
    return BALANCES


def BuildData(key, c_address, returned, BLOCK, lastBlock):
    with open(f'results/BALANCES_{key}.json') as B_json:
        BALANCES = json.load(B_json)
    with open(f'results/lastBALANCES_{key}.json') as B_json:
        lastBALANCES = json.load(B_json)
    price = getPrice(c_address, BLOCK)
    BALANCES = convertBalances(price, BALANCES)
    lastPrice = getPrice(c_address, lastBlock)
    lastBALANCES = convertBalances(lastPrice, lastBALANCES)
    print(
        f"Total of {sum(BALANCES.values())/1e18} tokens were Provided as Liq.")

    WITHDRAWALS = getWithdrawals(c_address, BLOCK, lastBlock)
    df = buildReport(BALANCES, WITHDRAWALS, returned, lastBALANCES, BLOCK)
    df[["returned", "withdrawn", "loss", "current", f"bal_on_{BLOCK}"]] = df[[
        "returned", "withdrawn", "loss", "current", f"bal_on_{BLOCK}"]].apply(lambda x: x/1e18)

    cr = df['current'].sum()
    print(cr)
    print(
        f"Total Loss: {(df['loss'].sum()-(cr))}, returned: {df['returned'].sum()}, ratio:  {df['returned'].sum()/(df['loss'].sum()-(cr))*100} %")
    df.to_excel(f"results/OUTPUT_{key}.xlsx")

    loss = df[['returned']].copy()
    loss.to_csv(f"results/final/FINAL_{key}.csv", float_format='%.18f')
