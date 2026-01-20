# ⚙️ NFT铸造系统配置指南

本文档详细说明NFT铸造系统所有配置项和部署步骤。

## 📋 目录

1. [环境要求](#环境要求)
2. [配置项说明](#配置项说明)
3. [智能合约部署](#智能合约部署)
4. [常见问题](#常见问题)

---

## 环境要求

### 基础环境

| 组件 | 版本要求 | 用途 |
|------|----------|------|
| Python | 3.8+ | 运行Flask应用 |
| Node.js | 16++ | 编译Solidity合约（Foundry） |
| Git | 最新版 | 克隆代码仓库 |

### 依赖工具

| 工具 | 安装命令 | 用途 |
|------|----------|------|
| Foundry | `curl -L https://foundry.paradigm.xyz \| bash` | Solidity编译和部署 |
| MetaMask | 浏览器插件 | 用户钱包连接 |

---

## 配置项说明

### 创建配置文件

```bash
cd nft_minter
cp .env.example .env
nano .env  # 编辑配置
```

### 完整配置示例

```ini
# ========== 网络选择 ==========
# amoy - Polygon Amoy 测试网 (推荐用于开发测试)
# polygon - Polygon 主网 (正式环境)
NETWORK=amoy

# ========== 合约配置 ==========
# 部署合约后，将合约地址填入此处
CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890

# ========== RPC 节点配置 ==========
# 默认使用公共节点，生产环境建议使用 Infura 或 Alchemy
# 测试网 RPC
RPC_URL_AMOY=https://rpc-amoy.polygon.technology
# 主网 RPC
RPC_URL_POLYGON=https://polygon-rpc.com

# ========== 钱包私钥 ==========
# 警告：此私钥用于后端签名部署合约
# 生产环境请使用专用部署钱包，勿使用存有大资金的钱包！
# 获取方式：MetaMask -> 账户详情 -> 导出私钥
PRIVATE_KEY=你的私钥_0x开头_不带0x前缀

# ========== IPFS 配置 (Pinata) ==========
# 推荐使用 JWT 认证，更安全
# 获取方式：登录 Pinata → API Keys → Create New Key
PINATA_JWT=your_jwt_token_here

# 或使用 API Key + Secret（旧方式）
PINATA_API_KEY=your_api_key
PINATA_API_SECRET=your_api_secret

# ========== NFT 元数据配置 ==========
NFT_NAME=Birthday Memorial
NFT_SYMBOL=BDAY
# 基础URI指向IPFS上的图片文件夹
# 上传图片到IPFS后，将文件夹CID替换下面的示例CID
NFT_BASE_URI=ipfs://QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/

# ========== Gas 配置 ==========
GAS_LIMIT=300000      # Gas限制（每个NFT）
GAS_PRICE_GWEI=30    # Gas价格（Gwei）

# ========== Flask 应用配置 ==========
SECRET_KEY=your_random_secret_key_here
```

---

## 智能合约部署

### 第一步：安装 Foundry

```bash
# macOS/Linux
curl -L https://foundry.paradigm.xyz | bash

# 加载环境变量
source ~/.bashrc  # Linux/macOS bash
source ~/.zshrc   # macOS zsh

# 验证安装
forge --version
```

### 第二步：编译合约

```bash
cd nft_minter/contracts

# 编译合约
forge build

# 查看编译输出
ls -la out/
```

预期输出：
```
out/BirthdayNFT.sol/
├── BirthdayNFT.json    # ABI文件（需要复制到abi/目录）
└── BirthdayNFT.s.sol  # 可验证的源码
```

### 第三步：复制 ABI 文件

```bash
# 创建abi目录（如果不存在）
mkdir -p ../abi

# 复制ABI文件
cp out/BirthdayNFT.sol/BirthdayNFT.json ../abi/
```

### 第四步：部署合约

#### 方式一：通过 Web 界面部署（推荐）

1. 启动应用：
```bash
cd ..
python nft_minter/app.py
```

2. 访问管理页面：http://127.0.0.1:5002/admin

3. 填写部署信息：
   - NFT名称
   - NFT符号
   - 基础URI
   - 私钥
   - 网络选择

4. 点击"部署合约"

#### 方式二：使用 Foundry 命令行部署

```bash
cd contracts

# 部署到测试网
forge script script/Deploy.s.sol --rpc-url amoy --broadcast

# 部署到主网
forge script script/Deploy.s.sol --rpc-url polygon --broadcast
```

部署后会输出合约地址，复制到 `.env` 的 `CONTRACT_ADDRESS`。

---

## MetaMask 配置

### 添加 Polygon Amoy 测试网

1. 打开 MetaMask
2. 点击网络下拉菜单 → 添加网络
3. 手动添加网络：

| 字段 | 值 |
|------|-----|
| 网络名称 | Polygon Amoy Testnet |
| 新增 RPC URL | https://rpc-amoy.polygon.technology |
| 链 ID | 80001 |
| 货币符号 | MATIC |
| 区块浏览器 URL | https://amoy.polygonscan.com |

### 获取测试 MATIC

访问水龙头：https://faucet.polygon.technology/

---

## 获取测试 MATIC

### 推荐水龙头列表

| 水龙头 | 测试网 | 金额 |
|--------|--------|------|
| [Polygon Faucet](https://faucet.polygon.technology/) | Amoy | 0.1-1 MATIC |
| [QuickNode](https://faucet.quicknode.com/polygon) | Amoy | 0.01 MATIC |

---

## 获取 Pinata API 密钥

1. 注册 [Pinata](https://pinata.cloud/)
2. 登录后进入 [API Keys](https://app.pinata.cloud/keys) 页面
3. 点击 "New Key"
4. 选择 "Admin" 权限类型
5. 复制生成的 JWT Token

---

## 生产环境配置建议

### 1. 使用专用 RPC 节点

```ini
# Infura (推荐)
RPC_URL_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID

# Alchemy (推荐)
RPC_URL_POLYGON=https://polygon-mainnet.g.alchemy.com/v2/YOUR_PROJECT_ID
```

### 2. 分离环境

开发/测试使用 `.env.development`，生产使用 `.env.production`：

```bash
cp .env .env.development
cp .env .env.production

# 生产环境使用主网
```

### 3. 安全加固

- ✅ 使用环境变量管理所有密钥
- ✅ 私钥使用专用钱包，不存大额资金
- ✅ 定期更新依赖包
- ✅ 配置CORS只允许信任的域名
- ✅ 设置请求速率限制

---

## 完整部署检查清单

### 部署前检查

- [ ] Python 3.8+ 已安装
- [ ] Foundry 已安装并配置
- [ ] MetaMask 已安装并配置网络
- [ ] 钱包有足够 MATIC 支付 Gas（至少 0.1 MATIC）
- [ ] IPFS 服务已配置（Pinata）

### 配置检查

- [ ] `.env` 文件已创建
- [ ] `NETWORK` 已选择（amoy/polygon）
- [ ] `PRIVATE_KEY` 已配置（部署用）
- [ ] `PINATA_JWT` 已配置
- [ ] `CONTRACT_ADDRESS` 部署后已填入

### 部署检查

- [ ] 合约已编译 (`forge build`)
- [ ] ABI 文件已复制 (`abi/BirthdayNFT.json`)
- [ ] 合约已部署到链上
- [ ] 合约地址已配置到 `.env`
- [ ] 应用可以正常启动
- [ ] MetaMask 可以连接铸造NFT

### 测试检查

- [ ] 铸造测试NFT成功
- [ ] OpenSea 上可以查看NFT
- [ ] 年度限制功能正常（同年不能重复铸造）

---

## 常见问题

### Q1: 部署合约时报错 "insufficient funds"

**A:** 钱包中MATIC不足以支付Gas费用。

**解决方案：**
1. 从水龙头获取测试MATIC
2. 确保钱包地址有足够余额

---

### Q2: 无法连接到钱包

**A:** 检查以下配置：
- MetaMask是否已安装
- 是否添加了正确的网络
- 网络RPC是否配置正确

---

### Q3: NFT铸造成功但OpenSea看不到

**A:** OpenSea需要先索引合约。

**解决方案：**
1. 访问 [OpenSea Polygon测试网](https://testnets.opensea.io/)
2. 将合约地址提交手动验证

---

### Q4: 提示 "合约地址不存在"

**A:** 检查以下几点：
- 合约是否成功部署
- `.env` 中的 `CONTRACT_ADDRESS` 是否正确
- 网络选择是否正确（测试网/主网）

---

### Q5: IPFS上传失败

**A:** 检查 Pinata 配置：
- JWT Token 是否正确
- API Key 权限是否足够
- 网络连接是否正常

---

### Q6: Foundry 安装失败

**A:** 尝试以下替代方案：

```bash
# 使用 cargo 安装（需要先安装 Rust）
cargo install --git foundryup
foundryup
```

---

## 成本估算

### 单次铸造成本

| 网络 | Gas费用 | 美元估算 |
|------|---------|----------|
| Amoy 测试网 | ~0.000001 MATIC | <$0.01 |
| Polygon 主网 | ~300,000 Gas | ~$0.10-0.50 |

### 年度运营成本（估算）

| 项目 | 费用 |
|------|------|
| 域名 | $10-15/年 |
| 服务器 | $10-50/月 |
| RPC服务（免费额度） | $0 |
| IPFS Pinata | $0（有限免费）|
| Gas费用（100次铸造） | ~$10-50 |

**年度总计：约 $130-$600**

---

## 更新日志

### v1.0.0 (2026-01-20)

- ✅ 基础NFT铸造功能
- ✅ 年度铸造限制
- ✅ IPFS元数据存储
- ✅ Web管理后台
- ✅ MetaMask集成

---

## 技术支持

遇到问题请提交 Issue：
- 问题标题：`[NFT] 问题简述`
- 详细描述问题和操作步骤
- 附上错误日志
