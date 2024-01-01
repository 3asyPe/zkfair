import asyncio
from datetime import datetime
import json
import time
import aiohttp
import requests
from web3 import AsyncWeb3, Web3
from eth_account import Account as EthereumAccount
from web3.middleware import async_geth_poa_middleware
from loguru import logger
from eth_account.messages import encode_defunct

from settings import RPC, SLEEP


class ZkFair:
    def __init__(self, key: str):
        self.key = key
        self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(RPC),
            middlewares=[async_geth_poa_middleware]
        )
        self.address = EthereumAccount.from_key(key).address
        self.explorer = "https://scan.zkfair.io/address/"

    async def get_values(self):
        logger.info(f"Getting values for {self.address}")

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        message = encode_defunct(
            text=f"{timestamp}GET/api/airdrop?address={self.address.lower()}"
        )
        signature = self.w3.eth.account.sign_message(message, private_key=self.key)
        
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://airdrop.zkfair.io/api/airdrop??',
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                },
                params={
                    "address": self.address.lower(),
                    "API-SIGNATURE": signature.signature.hex(),
                    "TIMESTAMP": timestamp
                }
            )
            response_data = await response.json()
            if response_data["data"]["account_profit"]:
                return float(response_data["data"]["account_profit"]) / 10**18
            return 0
        

async def main():
    with open("keys.txt") as f:
        keys = [row.strip() for row in f if row.strip()]

    for key in keys:
        zkfair = ZkFair(key)
        total = await zkfair.get_values()
        string = f"[{zkfair.address}] Total airdrop: {total} ZKF"
        logger.info(string)
        with open("output.txt", "a") as f:
            f.write(string + "\n")

        await asyncio.sleep(SLEEP)


if __name__ == "__main__":
    asyncio.run(main())
