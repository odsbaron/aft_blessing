# -*- coding: utf-8 -*-
"""
NFT 铸造系统 - Flask Web 应用
"""

import os
import json
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from web3_handler import w3_handler
from ipfs_handler import get_ipfs_handler
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# 设置合约地址（如果已部署）
if Config.CONTRACT_ADDRESS:
    w3_handler.set_contract(Config.CONTRACT_ADDRESS)


# ========== 辅助函数 ==========

def generate_metadata(name, description, image_url, attributes=None):
    """生成 NFT 元数据"""
    metadata = {
        "name": name,
        "description": description,
        "image": image_url,
        "external_url": "https://your-website.com",
        "attributes": attributes or []
    }
    return metadata


def generate_token_uri(name, year, image_ipfs_hash=None):
    """生成 tokenURI（IPFS CID）"""
    # 这里简化处理，实际应该上传到 IPFS
    # 返回一个模拟的 URI
    if image_ipfs_hash:
        return f"ipfs://{image_ipfs_hash}"
    return f"ipfs://QmExample{year}{name}"


# ========== 路由 ==========

@app.route('/')
def index():
    """首页"""
    # 检查连接状态
    is_connected = w3_handler.is_connected()
    network_info = None

    if is_connected:
        network_info = w3_handler.get_network_info()

    return render_template('index.html',
                         is_connected=is_connected,
                         network_info=network_info,
                         contract_address=Config.CONTRACT_ADDRESS)


@app.route('/claim')
def claim():
    """领取 NFT 页面"""
    is_connected = w3_handler.is_connected()
    return render_template('claim.html',
                         is_connected=is_connected,
                         contract_address=Config.CONTRACT_ADDRESS)


@app.route('/api/status')
def api_status():
    """获取系统状态 API"""
    return jsonify({
        'connected': w3_handler.is_connected(),
        'network': w3_handler.get_network_info() if w3_handler.is_connected() else None,
        'contract': Config.CONTRACT_ADDRESS,
        'chain_id': Config.get_chain_id(),
        'explorer': Config.get_explorer_url()
    })


@app.route('/api/check/<address>')
def api_check(address):
    """检查地址是否已铸造 NFT"""
    if not w3_handler.is_connected():
        return jsonify({'error': '未连接到区块链'}), 500

    has_minted = w3_handler.has_minted_this_year(address)

    if has_minted is None:
        return jsonify({'error': '合约未初始化'}), 500

    return jsonify({
        'address': address,
        'has_minted': has_minted,
        'current_year': w3_handler.get_current_year()
    })


@app.route('/api/tokens/<address>')
def api_tokens(address):
    """获取地址拥有的 NFT"""
    if not w3_handler.is_connected():
        return jsonify({'error': '未连接到区块链'}), 500

    tokens = w3_handler.get_user_tokens(address)

    if tokens is None:
        return jsonify({'error': '合约未初始化'}), 500

    token_details = []
    for token_id in tokens:
        uri = w3_handler.get_token_uri(token_id)
        token_details.append({
            'token_id': token_id,
            'uri': uri
        })

    return jsonify({
        'address': address,
        'tokens': token_details,
        'total': len(tokens)
    })


@app.route('/api/prepare-tx', methods=['POST'])
def api_prepare_tx():
    """准备铸造交易（前端签名）"""
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({'error': '缺少地址参数'}), 400

    if not w3_handler.is_connected():
        return jsonify({'error': '未连接到区块链'}), 500

    # 检查是否已铸造
    has_minted = w3_handler.has_minted_this_year(address)
    if has_minted:
        return jsonify({'error': '您今年已经领取过生日 NFT 了'}), 400

    # 生成 tokenURI
    year = w3_handler.get_current_year() or datetime.now().year
    token_uri = generate_token_uri("BirthdayNFT", year)

    # 准备交易
    transaction, error = w3_handler.prepare_mint_transaction(address, token_uri)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'transaction': transaction,
        'chain_id': Config.get_chain_id(),
        'token_uri': token_uri
    })


@app.route('/api/mint', methods=['POST'])
def api_mint():
    """后端签名并发送交易（使用服务器私钥）"""
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({'error': '缺少地址参数'}), 400

    if not Config.PRIVATE_KEY:
        return jsonify({'error': '服务器未配置私钥，请使用前端签名模式'}), 500

    if not w3_handler.is_connected():
        return jsonify({'error': '未连接到区块链'}), 500

    # 检查是否已铸造
    has_minted = w3_handler.has_minted_this_year(address)
    if has_minted:
        return jsonify({'error': '您今年已经领取过生日 NFT 了'}), 400

    # 生成 tokenURI
    year = w3_handler.get_current_year() or datetime.now().year
    token_uri = generate_token_uri("BirthdayNFT", year)

    # 准备交易
    transaction, error = w3_handler.prepare_mint_transaction(address, token_uri)
    if error:
        return jsonify({'error': error}), 500

    # 发送交易
    result, error = w3_handler.send_transaction(transaction, Config.PRIVATE_KEY)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'success': True,
        'tx_hash': result['tx_hash'],
        'explorer_url': result['explorer_url']
    })


@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    """部署新合约"""
    data = request.get_json()
    private_key = data.get('private_key')
    nft_name = data.get('name', Config.NFT_NAME)
    nft_symbol = data.get('symbol', Config.NFT_SYMBOL)
    base_uri = data.get('baseUri', Config.NFT_BASE_URI)

    if not private_key:
        return jsonify({'error': '缺少私钥参数'}), 400

    if not w3_handler.is_connected():
        return jsonify({'error': '未连接到区块链'}), 500

    result, error = w3_handler.deploy_contract(
        private_key, nft_name, nft_symbol, base_uri
    )

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'success': True,
        'contract_address': result['contract_address'],
        'tx_hash': result['tx_hash'],
        'explorer_url': result['explorer_url']
    })


# ========== IPFS API ==========

@app.route('/api/ipfs/test', methods=['GET'])
def api_ipfs_test():
    """测试 IPFS 连接"""
    ipfs = get_ipfs_handler()
    result = ipfs.test_connection()
    return jsonify(result)


@app.route('/api/ipfs/upload', methods=['POST'])
def api_ipfs_upload():
    """上传文件到 IPFS

    支持:
    - file: 文件上传
    - base64: Base64 编码的图片数据
    - url: 图片 URL (会先下载)
    """
    ipfs = get_ipfs_handler()

    # 检查是否配置了 API
    if not ipfs.jwt_key and not (ipfs.api_key and ipfs.api_secret):
        return jsonify({'error': '未配置 Pinata API 凭据'}), 400

    try:
        # 文件上传
        if 'file' in request.files:
            file = request.files['file']
            filename = file.filename or 'uploaded_file'

            # 保存临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
                file.save(tmp.name)
                result = ipfs.upload_file(tmp.name, filename)
                os.unlink(tmp.name)
                return jsonify({'success': True, **result})

        # Base64 上传
        data = request.get_json()
        if data and 'base64' in data:
            filename = data.get('filename', 'image.png')
            result = ipfs.upload_base64(data['base64'], filename)
            return jsonify({'success': True, **result})

        # URL 上传
        if data and 'url' in data:
            # 下载图片
            response = requests.get(data['url'], timeout=30)
            if response.status_code == 200:
                import tempfile
                filename = data.get('filename', 'downloaded_image.png')

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    tmp.write(response.content)
                    result = ipfs.upload_file(tmp.name, filename)
                    os.unlink(tmp.name)
                    return jsonify({'success': True, **result})
            else:
                return jsonify({'error': f'下载图片失败: {response.status_code}'}), 400

        return jsonify({'error': '请提供文件、base64 数据或图片 URL'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ipfs/metadata', methods=['POST'])
def api_ipfs_metadata():
    """创建 NFT 元数据并上传到 IPFS"""
    ipfs = get_ipfs_handler()

    # 检查是否配置了 API
    if not ipfs.jwt_key and not (ipfs.api_key and ipfs.api_secret):
        return jsonify({'error': '未配置 Pinata API 凭据'}), 400

    data = request.get_json()
    name = data.get('name', 'Birthday NFT')
    description = data.get('description', 'A special birthday NFT')
    image_cid = data.get('image_cid')
    attributes = data.get('attributes')

    if not image_cid:
        return jsonify({'error': '缺少 image_cid 参数'}), 400

    try:
        result = ipfs.create_nft_metadata(name, description, image_cid, attributes)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ipfs/list', methods=['GET'])
def api_ipfs_list():
    """获取 IPFS 文件列表"""
    ipfs = get_ipfs_handler()

    if not ipfs.jwt_key and not (ipfs.api_key and ipfs.api_secret):
        return jsonify({'error': '未配置 Pinata API 凭据'}), 400

    try:
        page_size = request.args.get('limit', 20, type=int)
        page_offset = request.args.get('offset', 0, type=int)

        files = ipfs.list_files(page_size=page_size, page_offset=page_offset)
        return jsonify({'success': True, 'files': files, 'count': len(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ipfs/delete/<cid>', methods=['DELETE'])
def api_ipfs_delete(cid):
    """从 IPFS 删除文件"""
    ipfs = get_ipfs_handler()

    if not ipfs.jwt_key and not (ipfs.api_key and ipfs.api_secret):
        return jsonify({'error': '未配置 Pinata API 凭据'}), 400

    try:
        success = ipfs.delete_file(cid)
        if success:
            return jsonify({'success': True, 'message': f'已删除 {cid}'})
        else:
            return jsonify({'error': '删除失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/my-nfts')
def my_nfts():
    """我的 NFT 页面"""
    return render_template('my_nfts.html',
                         contract_address=Config.CONTRACT_ADDRESS)


@app.route('/admin')
def admin():
    """管理后台"""
    return render_template('admin.html',
                         is_connected=w3_handler.is_connected(),
                         network_info=w3_handler.get_network_info() if w3_handler.is_connected() else None,
                         contract_address=Config.CONTRACT_ADDRESS)


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='页面不存在'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='服务器错误'), 500


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         🎨 NFT 铸造系统 🎨                             ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    print(f"网络: {Config.NETWORK}")
    print(f"RPC: {Config.get_rpc_url()}")
    print(f"Chain ID: {Config.get_chain_id()}")
    print(f"合约地址: {Config.CONTRACT_ADDRESS or '未部署'}")
    print(f"连接状态: {'✅ 已连接' if w3_handler.is_connected() else '❌ 未连接'}")
    print(f"\n🌐 管理界面: http://127.0.0.1:5002")

    app.run(host='0.0.0.0', port=5002, debug=True)
