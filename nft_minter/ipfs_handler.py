# -*- coding: utf-8 -*-
"""
IPFS 处理模块
支持通过 Pinata 或其他 IPFS 网关上传和检索文件
"""

import os
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, List
from config import Config


class IPFSHandler:
    """
    IPFS 文件处理器

    支持的功能:
    - 上传文件到 IPFS (通过 Pinata API)
    - 上传 Base64 数据
    - 获取文件网关 URL
    - 获取 Pinata 文件列表
    - 删除 Pinata 文件
    """

    def __init__(self):
        # Pinata API 配置
        self.api_key = getattr(Config, 'PINATA_API_KEY', None)
        self.api_secret = getattr(Config, 'PINATA_API_SECRET', None)
        self.jwt_key = getattr(Config, 'PINATA_JWT', None)

        # API 端点
        self.pinata_api = "https://api.pinata.cloud"
        self.gateway = "https://gateway.pinata.cloud/ipfs"

        # 备用公共网关
        self.fallback_gateways = [
            "https://ipfs.io/ipfs",
            "https://cloudflare-ipfs.com/ipfs",
            "https://dweb.link/ipfs"
        ]

    def _get_headers(self) -> Dict[str, str]:
        """获取 API 请求头"""
        if self.jwt_key:
            return {'Authorization': f'Bearer {self.jwt_key}'}
        elif self.api_key and self.api_secret:
            return {
                'pinata_api_key': self.api_key,
                'pinata_secret_api_key': self.api_secret
            }
        else:
            raise Exception("未配置 Pinata API 凭据")

    def upload_file(self, file_path: str, name: Optional[str] = None) -> Dict[str, str]:
        """
        上传文件到 IPFS

        Args:
            file_path: 文件路径
            name: 可选的文件名（Pinata 元数据）

        Returns:
            dict: {cid, url, gateway_url}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        filename = name or os.path.basename(file_path)

        # 准备文件和数据
        with open(file_path, 'rb') as f:
            files = {
                'file': (filename, f)
            }

            # Pinata 元数据
            metadata = {
                'name': filename,
                'keyvalues': {
                    'app': 'birthday-nft-system',
                    'type': 'nft-image'
                }
            }

            headers = self._get_headers()

            response = requests.post(
                f"{self.pinata_api}/pinning/pinFileToIPFS",
                files=files,
                data={'pinataMetadata': json.dumps(metadata)},
                headers=headers
            )

        if response.status_code == 200:
            result = response.json()
            cid = result['IpfsHash']
            return {
                'cid': cid,
                'url': f"ipfs://{cid}",
                'gateway_url': f"{self.gateway}/{cid}",
                'size': result.get('PinSize', 0)
            }
        else:
            raise Exception(f"上传失败: {response.status_code} - {response.text}")

    def upload_json(self, data: Dict, name: str = "metadata") -> Dict[str, str]:
        """
        上传 JSON 数据到 IPFS

        Args:
            data: Python 字典数据
            name: 文件名（用于元数据）

        Returns:
            dict: {cid, url, gateway_url}
        """
        headers = self._get_headers()
        headers['Content-Type'] = 'application/json'

        metadata = {
            'name': name,
            'keyvalues': {
                'app': 'birthday-nft-system',
                'type': 'nft-metadata'
            }
        }

        payload = {
            'pinataMetadata': metadata,
            'pinataContent': data
        }

        response = requests.post(
            f"{self.pinata_api}/pinning/pinJSONToIPFS",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            cid = result['IpfsHash']
            return {
                'cid': cid,
                'url': f"ipfs://{cid}",
                'gateway_url': f"{self.gateway}/{cid}"
            }
        else:
            raise Exception(f"上传失败: {response.status_code} - {response.text}")

    def upload_base64(self, base64_data: str, filename: str = "image.png") -> Dict[str, str]:
        """
        上传 Base64 编码的图片数据到 IPFS

        Args:
            base64_data: Base64 编码的图片数据
            filename: 文件名

        Returns:
            dict: {cid, url, gateway_url}
        """
        # 解码 Base64
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]

        image_data = base64.b64decode(base64_data)

        # 准备上传
        files = {
            'file': (filename, image_data)
        }

        metadata = {
            'name': filename,
            'keyvalues': {
                'app': 'birthday-nft-system',
                'type': 'nft-image'
            }
        }

        headers = self._get_headers()

        response = requests.post(
            f"{self.pinata_api}/pinning/pinFileToIPFS",
            files=files,
            data={'pinataMetadata': json.dumps(metadata)},
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            cid = result['IpfsHash']
            return {
                'cid': cid,
                'url': f"ipfs://{cid}",
                'gateway_url': f"{self.gateway}/{cid}",
                'size': result.get('PinSize', 0)
            }
        else:
            raise Exception(f"上传失败: {response.status_code} - {response.text}")

    def create_nft_metadata(
        self,
        name: str,
        description: str,
        image_cid: str,
        attributes: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        创建并上传 NFT 元数据到 IPFS

        Args:
            name: NFT 名称
            description: NFT 描述
            image_cid: 图片 CID
            attributes: NFT 属性列表

        Returns:
            dict: {cid, url, gateway_url, metadata}
        """
        metadata = {
            "name": name,
            "description": description,
            "image": f"ipfs://{image_cid}",
            "external_url": "https://your-website.com",  # 替换为实际网站
            "attributes": attributes or [
                {
                    "trait_type": "Type",
                    "value": "Birthday NFT"
                },
                {
                    "trait_type": "Year",
                    "value": str(__import__('datetime').datetime.now().year)
                }
            ]
        }

        result = self.upload_json(metadata, f"{name}-metadata")

        return {
            **result,
            'metadata': metadata
        }

    def get_gateway_url(self, cid: str, gateway_index: int = 0) -> str:
        """
        获取 IPFS 内容的网关 URL

        Args:
            cid: IPFS CID
            gateway_index: 使用的网关索引（0=默认Pinata）

        Returns:
            str: 网关 URL
        """
        if gateway_index == 0:
            return f"{self.gateway}/{cid}"
        else:
            gateway = self.fallback_gateways[min(gateway_index - 1, len(self.fallback_gateways) - 1)]
            return f"{gateway}/{cid}"

    def list_files(self, page_size: int = 50, page_offset: int = 0) -> List[Dict]:
        """
        列出 Pinata 上已上传的文件

        Args:
            page_size: 每页数量
            page_offset: 偏移量

        Returns:
            list: 文件列表
        """
        headers = self._get_headers()

        params = {
            'pageLimit': page_size,
            'pageOffset': page_offset
        }

        response = requests.get(
            f"{self.pinata_api}/data/pinList",
            params=params,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('rows', [])
        else:
            raise Exception(f"获取文件列表失败: {response.status_code} - {response.text}")

    def delete_file(self, cid: str) -> bool:
        """
        从 Pinata 取消固定（删除）文件

        Args:
            cid: IPFS CID

        Returns:
            bool: 是否成功
        """
        headers = self._get_headers()

        response = requests.delete(
            f"{self.pinata_api}/pinning/unpin/{cid}",
            headers=headers
        )

        return response.status_code == 200

    def test_connection(self) -> Dict[str, any]:
        """
        测试 Pinata API 连接

        Returns:
            dict: {success, message, configured}
        """
        try:
            if not self.jwt_key and not (self.api_key and self.api_secret):
                return {
                    'success': False,
                    'configured': False,
                    'message': '未配置 Pinata API 凭据'
                }

            # 尝试获取文件列表测试连接
            files = self.list_files(page_size=1)

            return {
                'success': True,
                'configured': True,
                'message': f'连接成功，已上传 {len(files)} 个文件'
            }
        except Exception as e:
            return {
                'success': False,
                'configured': True,
                'message': f'连接失败: {str(e)}'
            }


# 全局单例
_ipfs_handler_instance = None


def get_ipfs_handler():
    """获取全局 IPFS 处理器实例"""
    global _ipfs_handler_instance
    if _ipfs_handler_instance is None:
        _ipfs_handler_instance = IPFSHandler()
    return _ipfs_handler_instance


# 测试代码
if __name__ == "__main__":
    print("📁 IPFS 处理器测试")
    print("=" * 40)

    handler = IPFSHandler()

    # 测试连接
    test_result = handler.test_connection()
    print(f"连接测试: {test_result}")

    if test_result['success']:
        # 列出已有文件
        files = handler.list_files(page_size=5)
        print(f"\n已有文件 ({len(files)} 个):")
        for f in files[:5]:
            print(f"  - {f.get('metadata', {}).get('name', f['ipfs_hash'][:16])}: {f['ipfs_hash']}")
