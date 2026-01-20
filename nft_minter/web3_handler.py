# -*- coding: utf-8 -*-
"""
Web3 交互模块
处理区块链交互、NFT 铸造等
"""

import json
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from config import Config


class Web3Handler:
    """Web3 交互处理器"""

    def __init__(self):
        """初始化 Web3 连接"""
        self.w3 = Web3(Web3.HTTPProvider(Config.get_rpc_url()))

        # 添加 POA 中间件 (Polygon 使用 POA)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.contract_address = None
        self.contract = None

        # 加载合约 ABI
        self.abi = self._load_contract_abi()

    def _load_contract_abi(self):
        """加载合约 ABI"""
        abi_path = Config.CONTRACT_ABI_FILE

        # 如果文件存在，从文件加载
        if os.path.exists(abi_path):
            with open(abi_path, 'r', encoding='utf-8') as f:
                contract_data = json.load(f)
                return contract_data.get('abi', [])

        # 否则返回空（需要先部署合约）
        return []

    def set_contract(self, contract_address):
        """设置合约地址并初始化合约实例"""
        self.contract_address = contract_address
        if self.abi:
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.abi
            )
            return True
        return False

    def is_connected(self):
        """检查是否连接到区块链"""
        return self.w3.is_connected()

    def get_network_info(self):
        """获取网络信息"""
        if not self.is_connected():
            return None

        return {
            'chain_id': self.w3.eth.chain_id,
            'latest_block': self.w3.eth.block_number,
            'gas_price': self.w3.eth.gas_price,
        }

    def get_account_balance(self, address):
        """获取账户余额 (单位: MATIC)"""
        if not self.is_connected():
            return None

        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')

    def get_current_year(self):
        """获取当前年份（区块链时间）"""
        if not self.contract:
            return None
        try:
            return self.contract.functions.getCurrentYear().call()
        except Exception:
            # 如果合约未部署，返回本地计算的年份
            import datetime
            return datetime.datetime.now().year

    def has_minted_this_year(self, address):
        """检查地址今年是否已铸造 NFT"""
        if not self.contract:
            return None
        try:
            return self.contract.functions.hasMintedThisYear(address).call()
        except Exception as e:
            print(f"Error checking mint status: {e}")
            return None

    def get_user_tokens(self, address):
        """获取用户拥有的 NFT"""
        if not self.contract:
            return None
        try:
            tokens = self.contract.functions.getTokensByOwner(address).call()
            return tokens
        except Exception as e:
            print(f"Error getting tokens: {e}")
            return []

    def get_token_uri(self, token_id):
        """获取 NFT 元数据 URI"""
        if not self.contract:
            return None
        try:
            return self.contract.functions.tokenURI(token_id).call()
        except Exception as e:
            print(f"Error getting token URI: {e}")
            return None

    def prepare_mint_transaction(self, from_address, token_uri):
        """准备铸造交易"""
        if not self.contract:
            return None, '合约未初始化'

        try:
            # 构建交易
            transaction = self.contract.functions.mintBirthdayNFT(
                from_address,
                token_uri
            ).build_transaction({
                'from': from_address,
                'gas': Config.GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_address),
            })

            return transaction, None
        except Exception as e:
            return None, str(e)

    def send_transaction(self, transaction, private_key):
        """发送已签名的交易"""
        try:
            # 签名交易
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key
            )

            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=120
            )

            return {
                'success': tx_receipt['status'] == 1,
                'tx_hash': tx_hash.hex(),
                'receipt': tx_receipt,
                'explorer_url': f"{Config.get_explorer_url()}/tx/{tx_hash.hex()}"
            }, None

        except Exception as e:
            return None, str(e)

    def deploy_contract(self, private_key, nft_name, nft_symbol, base_uri):
        """部署新合约"""
        try:
            # 加载完整的合约 ABI 和 Bytecode
            abi_path = Config.CONTRACT_ABI_FILE
            if not os.path.exists(abi_path):
                return None, '合约文件不存在，请先编译合约'

            with open(abi_path, 'r', encoding='utf-8') as f:
                contract_data = json.load(f)

            # 创建合约实例
            Contract = self.w3.eth.contract(
                abi=contract_data['abi'],
                bytecode=contract_data['bytecode']
            )

            # 获取账户
            account = Account.from_key(private_key)
            address = account.address

            # 构建部署交易
            constructor = Contract.constructor(
                nft_name,
                nft_symbol,
                base_uri
            )

            transaction = constructor.build_transaction({
                'from': address,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(address),
            })

            # 签名并发送
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key
            )

            tx_hash = self.w3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            # 等待确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=300
            )

            if tx_receipt['status'] == 1:
                contract_address = tx_receipt['contractAddress']
                return {
                    'contract_address': contract_address,
                    'tx_hash': tx_hash.hex(),
                    'explorer_url': f"{Config.get_explorer_url()}/address/{contract_address}"
                }, None
            else:
                return None, '部署失败'

        except Exception as e:
            return None, str(e)


# 全局实例
w3_handler = Web3Handler()


# 测试代码
if __name__ == '__main__':
    print("=== Web3 连接测试 ===")

    handler = Web3Handler()

    print(f"连接状态: {handler.is_connected()}")

    if handler.is_connected():
        info = handler.get_network_info()
        print(f"Chain ID: {info['chain_id']}")
        print(f"最新区块: {info['latest_block']}")
        print(f"Gas 价格: {info['gas_price']}")
