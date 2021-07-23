# Reimbursement Calculation for the Lps

SharedStake suffered from an Insider Exploit on 23rd June 2021.
This calculation is implemented to distribute the returned tokens back to the community.

## Code Flow

- 1: findEveryone: code first reads all the addresses that held Uniswap LP tokens.
- 2: getSnapshot: using an archive node we get the plain balances and staked amounts for all of the addresses and filter some blacklisted addresses, such as developers, contracts or whose balances!>0
- 3: buildData: calculates the total damage, individual damages and returned amounts for every address with some additional stats

- create a secret.json file in data/ with access point to archive nodes, I used:

```
{"provider":"https://eth-mainnet.alchemyapi.io/v2/your-code"}
```

to run locally:

```
apt-get install python3-venv
python3 -m venv env
source env/bin/activate
pip install requirements.txt
python RUN.py

```

## Output

Output is shown in .xlsx format. Also the printed lines should be noted for stats.
Example:

```
snapshot Block:12688511,last Block:12881660

LP token : ETH_UNI
Unique address count : 449
Addresses w balance on Snapshot: 127
Total of 3289778062055932810260 LP tokens.
Total of 102.29697003994364 tokens were Provided as Liq.
total withdrawals: 12.303429382375178
Total Loss: 80.51109831252137, returned: 27.0, ratio:  33.53574918974974 %

LP token : vETH2_UNI
Unique address count : 107
Addresses w balance on Snapshot: 58
Total of 4739998936952645723172 LP tokens.
Total of 148.66982032805763 tokens were Provided as Liq.
total withdrawals: 30.125608482028483
Total Loss: 109.9108993673719, returned: 101.14731789866241, ratio:  92.02664929579218 %
DONE
```
