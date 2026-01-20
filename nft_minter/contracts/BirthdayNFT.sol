// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title BirthdayNFT
 * @dev 年度生日纪念 NFT 合约
 * 每个地址每年只能铸造一次生日 NFT
 */
contract BirthdayNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    // 记录每个地址每年是否已铸造 (地址 => 年份 => bool)
    mapping(address => mapping(uint256 => bool)) private _mintedYears;

    // 基础 URI (可通过 setBaseURI 更新)
    string private _baseTokenURI;

    // 铸造价格 (单位: wei)
    uint256 public mintPrice = 0;

    // 当前年份 (用于检查)
    uint256 public currentYear;

    // 事件
    event BirthdayNFTMinted(address indexed recipient, uint256 tokenId, uint256 year);
    event BaseURIUpdated(string newBaseURI);
    event MintPriceUpdated(uint256 newPrice);

    constructor(
        string memory name,
        string memory symbol,
        string memory baseURI
    ) ERC721(name, symbol) Ownable(msg.sender) {
        _baseTokenURI = baseURI;
        currentYear = getCurrentYear();
    }

    /**
     * @dev 获取当前年份
     */
    function getCurrentYear() public view returns (uint256) {
        return block.timestamp / 365 days;
    }

    /**
     * @dev 更新当前年份 (可由任何人调用以保持同步)
     */
    function updateCurrentYear() public {
        uint256 newYear = block.timestamp / 365 days;
        if (newYear > currentYear) {
            currentYear = newYear;
        }
    }

    /**
     * @dev 铸造生日 NFT
     * @param to 接收地址
     * @param tokenURI 元数据 URI
     */
    function mintBirthdayNFT(address to, string memory tokenURI) external returns (uint256) {
        // 确保每年只能铸造一次
        updateCurrentYear();
        uint256 year = getCurrentYear();

        require(!_mintedYears[to][year], "You have already minted this year's NFT");

        // 铸造 NFT
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);

        // 标记已铸造
        _mintedYears[to][year] = true;

        emit BirthdayNFTMinted(to, tokenId, year);

        return tokenId;
    }

    /**
     * @dev 批量铸造 (管理员专用，用于活动等)
     */
    function mintBatch(address[] memory recipients, string[] memory uris) external onlyOwner {
        require(recipients.length == uris.length, "Arrays length mismatch");

        for (uint256 i = 0; i < recipients.length; i++) {
            uint256 tokenId = _tokenIdCounter.current();
            _tokenIdCounter.increment();

            _safeMint(recipients[i], tokenId);
            _setTokenURI(tokenId, uris[i]);

            emit BirthdayNFTMinted(recipients[i], tokenId, currentYear);
        }
    }

    /**
     * @dev 检查地址在指定年份是否已铸造
     */
    function hasMintedInYear(address addr, uint256 year) external view returns (bool) {
        return _mintedYears[addr][year];
    }

    /**
     * @dev 检查地址今年是否已铸造
     */
    function hasMintedThisYear(address addr) external view returns (bool) {
        return _mintedYears[addr][getCurrentYear()];
    }

    /**
     * @dev 设置基础 URI
     */
    function setBaseURI(string memory baseURI) external onlyOwner {
        _baseTokenURI = baseURI;
        emit BaseURIUpdated(baseURI);
    }

    /**
     * @dev 返回基础 URI
     */
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    /**
     * @dev 设置铸造价格
     */
    function setMintPrice(uint256 newPrice) external onlyOwner {
        mintPrice = newPrice;
        emit MintPriceUpdated(newPrice);
    }

    /**
     * @dev 提取合约余额
     */
    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }

    /**
     * @dev 获取总供应量
     */
    function totalSupply() external view returns (uint256) {
        return _tokenIdCounter.current();
    }

    /**
     * @dev 获取用户的 NFT
     */
    function getTokensByOwner(address owner) external view returns (uint256[] memory) {
        uint256 balance = balanceOf(owner);
        uint256[] memory tokens = new uint256[](balance);
        uint256 index = 0;

        for (uint256 i = 0; i < _tokenIdCounter.current() && index < balance; i++) {
            if (_ownerOf(i) == owner) {
                tokens[index] = i;
                index++;
            }
        }

        return tokens;
    }

    // 覆盖 _ownerOf 以支持更高效的查询
    function _ownerOf(uint256 tokenId) internal view override returns (address) {
        return super.ownerOf(tokenId);
    }
}
