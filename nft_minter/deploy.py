# -*- coding: utf-8 -*-
"""
部署脚本
用于部署 BirthdayNFT 合约到 Polygon
"""

import os
import json
from web3 import Web3
from eth_account import Account
from config import Config


def deploy_contract():
    """部署合约到区块链"""

    print("=" * 60)
    print("  BirthdayNFT 合约部署工具")
    print("=" * 60)

    # 获取私钥
    private_key = os.getenv('PRIVATE_KEY') or input("\n请输入私钥 (0x...): ").strip()

    if not private_key.startswith('0x'):
        private_key = '0x' + private_key

    # 创建账户
    account = Account.from_key(private_key)
    print(f"\n部署账户: {account.address}")

    # 检查余额
    w3 = Web3(Web3.HTTPProvider(Config.get_rpc_url()))
    balance = w3.eth.get_balance(account.address)
    balance_matic = w3.from_wei(balance, 'ether')

    print(f"账户余额: {balance_matic} MATIC")

    if balance_matic < 0.1:
        print("\n⚠️  警告: 余额可能不足以支付 Gas 费用")
        confirm = input("是否继续? (yes/no): ")
        if confirm.lower() != 'yes':
            print("部署已取消")
            return

    # 读取合约文件
    abi_path = Config.CONTRACT_ABI_FILE

    if not os.path.exists(abi_path):
        print(f"\n❌ 错误: 找不到合约文件 {abi_path}")
        print("请先运行: forge build")
        return

    with open(abi_path, 'r', encoding='utf-8') as f:
        contract_data = json.load(f)

    if 'bytecode' not in contract_data:
        print("\n❌ 错误: 合约文件缺少 bytecode")
        print("请确保合约已正确编译")
        return

    # 创建合约实例
    Contract = w3.eth.contract(
        abi=contract_data['abi'],
        bytecode=contract_data['bytecode']
    )

    # NFT 配置
    nft_name = input(f"\nNFT 名称 [{Config.NFT_NAME}]: ").strip() or Config.NFT_NAME
    nft_symbol = input(f"NFT 符号 [{Config.NFT_SYMBOL}]: ").strip() or Config.NFT_SYMBOL
    base_uri = input(f"Base URI [{Config.NFT_BASE_URI}]: ").strip() or Config.NFT_BASE_URI

    print("\n" + "-" * 60)
    print("部署配置:")
    print(f"  名称: {nft_name}")
    print(f"  符号: {nft_symbol}")
    print(f"  Base URI: {base_uri}")
    print(f"  网络: {Config.NETWORK}")
    print("-" * 60)

    confirm = input("\n确认部署? (yes/no): ")
    if confirm.lower() != 'yes':
        print("部署已取消")
        return

    # 构建部署交易
    print("\n正在构建交易...")
    constructor = Contract.constructor(nft_name, nft_symbol, base_uri)

    transaction = constructor.build_transaction({
        'from': account.address,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    # 签名交易
    print("正在签名交易...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # 发送交易
    print("正在部署合约...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"\n✅ 交易已发送!")
    print(f"交易哈希: {tx_hash.hex()}")
    print(f"浏览器: {Config.get_explorer_url()}/tx/{tx_hash.hex()}")

    # 等待确认
    print("\n等待交易确认...")
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

        if receipt['status'] == 1:
            contract_address = receipt['contractAddress']
            print("\n" + "=" * 60)
            print("🎉 部署成功!")
            print("=" * 60)
            print(f"合约地址: {contract_address}")
            print(f"浏览器: {Config.get_explorer_url()}/address/{contract_address}")
            print("=" * 60)

            # 更新 .env 文件
            print(f"\n请将以下内容添加到 .env 文件:")
            print(f"CONTRACT_ADDRESS={contract_address}")

        else:
            print("\n❌ 部署失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == '__main__':
    deploy_contract()
