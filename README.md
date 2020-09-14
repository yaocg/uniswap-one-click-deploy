# Uniswap部署私有测试连

## 主要步骤
**搭建测试链**

1. 搭建私有测试链

**合约编译**

2. 编译 [Uniswap-v2-core](https://github.com/Uniswap/uniswap-v2-core.git) 项目(Factory/Erc20/Pair 合约)
3. 编译 [Uniswap-v2-periphery](https://github.com/Uniswap/uniswap-v2-periphery.git) 项目(Router/WETH 合约)
4. 编译 [Erc20 测试代币(Seacoin)](https://github.com/yaocg/truffle-create-erc20-seacoin-test.git) 合约

**合约部署**

5. 部署 Uniswap Factory 合约
6. 部署 WETH 合约
7. 部署 Uniswap Router 合约
8. 部署 Erc20 测试代币(Seacoin) 合约
9. 测试代币(Seacoin) 授权 Uniswap Router 合约

**合约测试**

10. Router 合约添加流动性
11. Factory 合约获取流动性


## 一键部署

**准备**

1. 搭建测试链
2. 合约编译

**执行一键部署脚本(合约部署、合约测试)**

```
python3 main.py -o
```

## python3 依赖包

```
pip3 install web3 --user --timeout=1500
```
