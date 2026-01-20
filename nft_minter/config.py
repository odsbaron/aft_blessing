# -*- coding: utf-8 -*-
"""
配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """配置类"""

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'nft-minter-secret-key-2024')

    # Web3 配置
    # Polygon RPC 节点
    POLYGON_RPC_URL = os.getenv(
        'POLYGON_RPC_URL',
        'https://polygon-rpc.com'
    )

    # 测试网 (Amoy) - 用于开发测试
    AMOY_RPC_URL = os.getenv(
        'AMOY_RPC_URL',
        'https://rpc-amoy.polygon.technology'
    )

    # 当前使用的网络 (polygon / amoy)
    NETWORK = os.getenv('NETWORK', 'amoy')  # 默认使用测试网

    # 合约配置
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    CONTRACT_ABI_FILE = os.path.join(
        os.path.dirname(__file__),
        'abi',
        'BirthdayNFT.json'
    )

    # 管理员私钥 (用于部署合约、批量铸造等)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')

    # IPFS 配置 (用于存储 NFT 元数据)
    IPFS_API_KEY = os.getenv('IPFS_API_KEY', '')
    IPFS_API_SECRET = os.getenv('IPFS_API_SECRET', '')
    # Pinata JWT (推荐使用)
    PINATA_JWT = os.getenv('PINATA_JWT', '')
    PINATA_API_KEY = os.getenv('PINATA_API_KEY', '')
    PINATA_API_SECRET = os.getenv('PINATA_API_SECRET', '')
    IPFS_GATEWAY = os.getenv(
        'IPFS_GATEWAY',
        'https://gateway.pinata.cloud/ipfs'
    )

    # NFT 元数据
    NFT_NAME = os.getenv('NFT_NAME', 'Birthday Memorial')
    NFT_SYMBOL = os.getenv('NFT_SYMBOL', 'BDAY')
    NFT_BASE_URI = os.getenv(
        'NFT_BASE_URI',
        'ipfs://QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/'
    )

    # 图片配置
    NFT_IMAGE_PATH = os.getenv(
        'NFT_IMAGE_PATH',
        os.path.join(os.path.dirname(__file__), 'static', 'nft-image.png')
    )

    # Gas 配置
    GAS_LIMIT = int(os.getenv('GAS_LIMIT', '300000'))
    GAS_PRICE_GWEI = int(os.getenv('GAS_PRICE_GWEI', '30'))

    @classmethod
    def get_rpc_url(cls):
        """获取当前网络的 RPC URL"""
        if cls.NETWORK == 'polygon':
            return cls.POLYGON_RPC_URL
        else:
            return cls.AMOY_RPC_URL

    @classmethod
    def get_chain_id(cls):
        """获取当前网络的 Chain ID"""
        if cls.NETWORK == 'polygon':
            return 137  # Polygon Mainnet
        else:
            return 80001  # Polygon Amoy Testnet

    @classmethod
    def get_explorer_url(cls):
        """获取区块浏览器 URL"""
        if cls.NETWORK == 'polygon':
            return 'https://polygonscan.com'
        else:
            return 'https://amoy.polygonscan.com'


# 测试配置
if __name__ == '__main__':
    print(f"Network: {Config.NETWORK}")
    print(f"RPC URL: {Config.get_rpc_url()}")
    print(f"Chain ID: {Config.get_chain_id()}")
    print(f"Explorer: {Config.get_explorer_url()}")
