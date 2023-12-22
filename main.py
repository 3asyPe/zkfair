import time
import requests
from loguru import logger


def get_values(address):
    logger.info(f"Getting values for {address}")
                
    response = requests.post(f'https://api.zkfair.io/data/api/community-airdrop?address={address.lower()}')

    if response.status_code == 200:
        json = response.json()
        return (
            float(json["community_airdrop"]["Polygon zkEVM"]["value_decimal"]),
            float(json["community_airdrop"]["Lumoz"]["value_decimal"]),
            float(json["community_airdrop"]["zkRollups"]["value_decimal"])
        )
    else:
        return 0, 0, 0
    

def main():
    with open("addresses.txt") as f:
        addresses = [row.strip() for row in f if row.strip()]

    for address in addresses:
        polygon, lumoz, zkrollups = get_values(address)
        string = f"[{address}] Polygon zkEVM: {polygon}, Lumoz: {lumoz}, zkRollups: {zkrollups}, Total: {polygon + lumoz + zkrollups}"
        logger.info(string)
        with open("output.txt", "a") as f:
            f.write(string + "\n")

        time.sleep(1)


if __name__ == "__main__":
    main()
