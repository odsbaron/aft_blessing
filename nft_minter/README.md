# 生日纪念 NFT 铸造系统

基于 Polygon 链的年度生日纪念 NFT 铸造系统，每个地址每年可免费领取一枚生日纪念 NFT。

## 功能特点

- **每年一次** - 每个地址每年只能铸造一次，确保纪念意义
- **免费铸造** - 部署在 Polygon，Gas 费用极低
- **钱包连接** - 支持 MetaMask 等主流钱包
- **用户自取** - 用户点击领取，简单便捷
- **统一模板** - 所有人领取相同的设计（可自定义）

## 项目结构

```
nft_minter/
├── contracts/          # Solidity 智能合约
│   └── BirthdayNFT.sol
├── templates/          # HTML 模板
├── static/             # CSS 样式
├── abi/                # 合约 ABI 文件
├── app.py              # Flask 应用
├── web3_handler.py     # Web3 交互模块
├── config.py           # 配置文件
└── requirements.txt    # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
cd nft_minter
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置网络和合约信息。

### 3. 编译智能合约

```bash
# 安装 Foundry (如果未安装)
curl -L https://foundry.paradigm.xyz | bash

# 编译合约
forge build

# 复制 ABI 到项目目录
cp out/BirthdayNFT.sol/BirthdayNFT.json abi/
```

### 4. 部署合约

**方式一：通过管理后台部署**

1. 启动应用：`python app.py`
2. 访问管理页面：http://127.0.0.1:5002/admin
3. 填入 NFT 信息和私钥，点击部署

**方式二：使用 Foundry 部署**

```bash
# 测试网部署
forge script script/Deploy.s.sol --rpc-url amoy --broadcast

# 主网部署
forge script script/Deploy.s.sol --rpc-url polygon --broadcast
```

### 5. 配置合约地址

将部署后的合约地址填入 `.env`：

```bash
CONTRACT_ADDRESS=0xYourContractAddress
```

### 6. 启动服务

```bash
python app.py
```

访问：http://127.0.0.1:5002

## 网络配置

### Polygon Amoy 测试网

| 配置项 | 值 |
|--------|-----|
| RPC URL | https://rpc-amoy.polygon.technology |
| Chain ID | 80001 |
| 区块浏览器 | https://amoy.polygonscan.com |
| 水龙头 | https://faucet.polygon.technology |

### Polygon 主网

| 配置项 | 值 |
|--------|-----|
| RPC URL | https://polygon-rpc.com |
| Chain ID | 137 |
| 区块浏览器 | https://polygonscan.com |

## 添加测试网络到 MetaMask

```javascript
// Network Name: Polygon Amoy Testnet
// RPC URL: https://rpc-amoy.polygon.technology
// Chain ID: 80001
// Currency Symbol: MATIC
```

## 自定义 NFT 图片

1. 将图片放入 `static/nft-image.png`
2. 上传到 IPFS（推荐使用 Pinata）
3. 获取 CID 后更新 `NFT_BASE_URI`

## API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/status` | 获取系统状态 |
| `GET /api/check/<address>` | 检查地址是否已铸造 |
| `GET /api/tokens/<address>` | 获取地址拥有的 NFT |
| `POST /api/prepare-tx` | 准备铸造交易 |
| `POST /api/mint` | 后端签名铸造 |
| `POST /api/deploy` | 部署新合约 |

## 安全提醒

- ⚠️ **永远不要私钥提交到代码仓库**
- ⚠️ **生产环境请使用硬件钱包**
- ⚠️ **测试网测试通过后再部署到主网**

## License

MIT
