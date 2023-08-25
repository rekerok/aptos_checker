import csv
from time import sleep
import tqdm
import requests

resource_type_info = "0x1::coin::CoinInfo"
resource_type_balance = "0x1::coin::CoinStore"

################# CONFIG #################
url = "https://rpc.ankr.com/http/aptos/v1"  # rpc
wallets = "wallets.txt"  # имя файла откуда брать адреса
to_file = "apt_balance.csv" # файл в который записывать балансы аптоса
tokens = {
    "apt": "0x1::aptos_coin::AptosCoin",
    "lz_usdc": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
    "lz_usdt": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDT",
    "w_usdc": "0x5e156f1207d0ebfa19a9eeff00d62a282278fb8719f4fab3a586a0a2c0fffbea::coin::T",
    "weth": "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::WETH",
    "tortuga": "0x84d7aeef42d38a5ffc3ccef853e1b82e4958659d16a7de736a29c55fbbeb0114::staked_aptos_coin::StakedAptosCoin",
    "ditto": "0xd11107bdf0d6d7040c6c0bfbdecb6545191fdf13e8d8d259952f53e1713f61b5::staked_coin::StakedAptos",
}
##########################################


def get_addr_token(full_loken):
    return full_loken.split("::")[0]

tokens_info = dict()

balances = dict()
for name, token_address in tokens.items():
    tokens_info[name] = requests.get(
        f"{url}/accounts/{get_addr_token(token_address)}/resource/{resource_type_info}<{token_address}>"
    ).json()

with open(wallets, "r") as file:
    adressess = [i.strip() for i in file.readlines()]

for address in tqdm.tqdm(adressess):
    balance = dict()
    for token_name, token_address in tokens_info.items():
        response = requests.get(
            f"{url}/accounts/{address}/resource/{resource_type_balance}<{tokens[token_name]}>"
        )
        if response.status_code == 200:
            value = int(response.json()["data"]["coin"]["value"])
            decimals = token_address["data"]["decimals"]
            balance[token_name] = value * 10 ** (-decimals)
        else:
            balance[token_name] = 0
    balances[address] = balance

with open(to_file, "w") as file:
    writer = csv.writer(file)
    writer.writerow(("number", "address", *tokens.keys()))
    counter = 1
    for address, balance in balances.items():
        writer.writerow(
            (
                counter,
                address,
                *[str(balance[i]).replace(".", ",") for i in balance.keys()],
            )
        )
        counter += 1
