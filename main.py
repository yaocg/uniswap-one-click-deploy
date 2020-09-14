from optparse import OptionParser
from optparse import OptionGroup

import sys
import json
import time
from web3 import Web3
import traceback
from web3.middleware import geth_poa_middleware

def connect_ethereum_node(geth_http):
    print("========== Connect Ethereum Node ==========")
    w3=None
    errinfo=None
    try:
        w3 = Web3(Web3.HTTPProvider(geth_http))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        print("geth version:", w3.clientVersion)
        print("connected:", w3.isConnected())
        print("accounts:", w3.geth.personal.list_accounts())
        print("")
    except:
        errinfo = "{}".format(traceback.format_exc())
    finally:
        return (w3, errinfo)

def get_abi_bytecode_from_contract_json_file(contract_json_file):
    abi=None
    bytecode=None
    errinfo=None
    try:
        with open(contract_json_file, "r") as rop:
            j_obj = json.loads(rop.read())
            for k, v in j_obj.items():
                if k.lower() == "abi":
                    abi=v
                elif k.lower() == "bytecode":
                    bytecode=v

        if abi is None or bytecode is None:
            errinfo = "can not find abi/bytecode ..."
    except:
        errinfo = "{}".format(traceback.format_exc())
    finally:
        return (abi, bytecode, errinfo)

def attach_contract(geth_http, contract_file, contract_address, tx_gas):
    print("========== attach_contract ==========")
    print("========== Params Begin ==========")
    print("geth_http:", geth_http)
    print("contract_file:", contract_file)
    print("contract_address:", contract_address)
    print("tx_gas:", tx_gas)
    print("========== Params End ==========")

    w3, errinfo = connect_ethereum_node(geth_http)
    if errinfo:
        print("function connect_ethereum_node get some err:{}".format(errinfo))
        return

    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(contract_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(contract_file) get some err:{}".format(errinfo))
        return

    contract_address = Web3.toChecksumAddress(contract_address)
    print("contract_address... ", contract_address)

    greeter = w3.eth.contract(
        address=contract_address,
        abi=abi)

    print("\n========== Run Contract Consle ==========")
    print("Enter -h for help ...")
    print_detail_cmd=0
    wait_transaction_receipt=1
    while 1:
        try:
            is_transaction=False
            v=input("attach_contract> ")
            if v.lower() == "-h":
                print("1. call contract function: -call.fun(arg1, arg2), default")
                print("2. transaction contract function: -transaction.fun(arg1, arg2)")
                print("3. ChecksumAddress: -toChecksumAddress(address)")
                print("4. waitForTransactionReceipt: -waitForTransactionReceipt(tx)")
                print("5. function list:", dir(greeter.functions))
                print("6. print detail cmd:", "-print_detail_cmd")
                print("6. wait transaction receipt:", "-waitForTransactionReceipt")
                continue
            elif not v:
                continue
            elif v.lstrip().find("-print_detail_cmd") == 0:
                print_detail_cmd=~print_detail_cmd

                print(True if print_detail_cmd else False)
                continue
            elif v.lstrip().find("-waitForTransactionReceipt") == 0:
                wait_transaction_receipt=~wait_transaction_receipt

                print(True if wait_transaction_receipt else False)
                continue
            elif v.lstrip().find("-toChecksumAddress") == 0:
                cmd = "Web3.{}".format(v.lstrip()[1:])
            elif v.lstrip().find("-waitForTransactionReceipt") == 0:
                cmd = "w3.eth.{}".format(v.lstrip()[1:])
            elif v.lstrip().find("-transaction.") == 0:
                cmd = "greeter.functions.{}.transact({})".format(v.lstrip()[13:], {"from": w3.eth.coinbase, "gas": tx_gas})
                is_transaction=True
            elif v.lstrip().find("-call.") == 0:
                cmd = "greeter.functions.{}.call()".format(v.lstrip()[6:])
            else:
                cmd = "greeter.functions.{}.call()".format(v)

            try:
                if print_detail_cmd:
                    print(cmd)
                res = eval(cmd)
                print("{}".format(res.hex() if str(type(res)) == "<class 'hexbytes.main.HexBytes'>" else res))
                if wait_transaction_receipt and is_transaction:
                    print("--- waitForTransactionReceipt ---")
                    tx_receipt = w3.eth.waitForTransactionReceipt(res.hex())
                    print(tx_receipt)
            except:
                print("{}".format(traceback.format_exc()))
        except (KeyboardInterrupt,EOFError):
            break

    print("\nrun_contract End...")

def deploy_contract(w3, abi, bytecode, args=[], tx_gas=8000000):
    tx_receipt=None
    errinfo=None
    try:
        print("---------- Deploy Contract Begin ----------")
        attached_contract_obj = w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = attached_contract_obj.constructor(*args).transact({"from": w3.eth.coinbase, "gas": tx_gas})

        print("submiting block, Wait ...")
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

        for item in tx_receipt.items():
            print("{}: {}".format(item[0], item[1].hex() if str(type(item[1])) == "<class 'hexbytes.main.HexBytes'>" else item[1]))
        print("---------- Deploy Contract {} End ----------".format( "Sucess!!!" if tx_receipt.status else "Failed!!!"))

        errinfo = None if tx_receipt.status else "Unknow err!!!"
    except:
        errinfo = "{}".format(traceback.format_exc())
    finally:
        return (tx_receipt, errinfo)

def one_click_deploy(geth_http, weth_file, factory_file, router_file, seacoin_file, pair_file, erc20_file, tx_gas):
    print("========== one_click_deploy ==========")
    print("========== Params Begin ==========")
    print("geth_http:", geth_http)
    print("weth_file:", weth_file)
    print("factory_file:", factory_file)
    print("router_file:", router_file)
    print("seacoin_file:", seacoin_file)
    print("pair_file:", pair_file)
    print("erc20_file:", erc20_file)
    print("tx_gas:", tx_gas)
    print("========== Params End ==========\n")

    w3, errinfo = connect_ethereum_node(geth_http)
    if errinfo:
        print("function connect_ethereum_node get some err:{}".format(errinfo))
        return

    print("========== Deploy Weth Begin ==========")
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(weth_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(weth) get some err:{}".format(errinfo))
        return

    weth_contract_tx, errinfo = deploy_contract(w3, abi, bytecode, [], tx_gas)
    if errinfo:
        print("function deploy_contract(weth) get some err:{}".format(errinfo))
        return

    print("weth_contract_address:", weth_contract_tx.contractAddress)
    print("========== Deploy Weth {} End ==========\n".format("Sucess!!!" if weth_contract_tx.status else "Failed!!!"))
    assert weth_contract_tx.status, "Deploy Weth Failed!!!"



    print("========== Deploy Factory Begin ==========")
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(factory_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(factory) get some err:{}".format(errinfo))
        return

    factory_contract_tx, errinfo = deploy_contract(w3, abi, bytecode, [w3.eth.coinbase], tx_gas)
    if errinfo:
        print("function deploy_contract(factory)  get some err:{}".format(errinfo))
        return

    factory_attached_contract_obj = w3.eth.contract(abi=abi, address=factory_contract_tx.contractAddress)

    print("factory_contract_address:", factory_contract_tx.contractAddress)
    print("========== Deploy Factory {} End ==========\n".format("Sucess!!!" if factory_contract_tx.status else "Failed!!!"))
    assert factory_contract_tx.status, "Deploy Factory Failed!!!"



    print("========== Deploy Router Begin ==========")
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(router_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(router) get some err:{}".format(errinfo))
        return

    router_contract_tx, errinfo = deploy_contract(w3, abi, bytecode, [factory_contract_tx.contractAddress, weth_contract_tx.contractAddress], tx_gas)
    if errinfo:
        print("function deploy_contract(router)  get some err:{}".format(errinfo))
        return

    router_attached_contract_obj = w3.eth.contract(abi=abi, address=router_contract_tx.contractAddress)
    print("router_contract_address:", router_contract_tx.contractAddress)
    print("router_contract_factory_address:", router_attached_contract_obj.functions.factory().call())
    print("router_contract_weth_address:", router_attached_contract_obj.functions.WETH().call())
    print("========== Deploy Router {} End ==========\n".format("Sucess!!!" if router_contract_tx.status else "Failed!!!"))
    assert router_contract_tx.status, "Deploy Router Failed!!!"




    print("========== Deploy Seacoin Begin ==========")
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(seacoin_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(seacoin) get some err:{}".format(errinfo))
        return

    seacoin_contract_tx, errinfo = deploy_contract(w3, abi, bytecode, [], tx_gas)
    if errinfo:
        print("function deploy_contract(seacoin) get some err:{}".format(errinfo))
        return

    print("seacoin_contract_address:", seacoin_contract_tx.contractAddress)
    print("========== Deploy Seacoin {} End ==========\n".format("Sucess!!!" if seacoin_contract_tx.status else "Failed!!!"))
    assert seacoin_contract_tx.status, "Deploy Seacoin Failed!!!"



    print("========== Seacoin Approve Router ==========")
    seacoin_attached_contract_obj = w3.eth.contract(abi=abi, address=seacoin_contract_tx.contractAddress)
    res=seacoin_attached_contract_obj.functions.approve(router_contract_tx.contractAddress, 100 * 10 ** 18).transact({"from": w3.eth.coinbase, "gas": tx_gas})
    seacoin_tx = w3.eth.waitForTransactionReceipt(res.hex())
    for item in seacoin_tx.items():
        print("{}: {}".format(item[0], item[1].hex() if str(type(item[1])) == "<class 'hexbytes.main.HexBytes'>" else item[1]))
    print("========== Seacoin Approve Router {} End ==========\n".format( "Sucess!!!" if seacoin_tx.status else "Failed!!!"))
    assert seacoin_tx.status, "Seacoin Approve Failed!!!"



    print("========== Router exec fun: addLiquidityETH(Seacoin-ETH) Begin ==========")
    res=router_attached_contract_obj.functions.addLiquidityETH(seacoin_contract_tx.contractAddress, 100 * 10 ** 18, 900 * 10 ** 17, 9 * 10 ** 17, w3.eth.coinbase, int(time.time())+300).transact({"from": w3.eth.coinbase, "gas": tx_gas, "value":1 * 10 ** 18})
    router_tx = w3.eth.waitForTransactionReceipt(res.hex())
    for item in router_tx.items():
        print("{}: {}".format(item[0], item[1].hex() if str(type(item[1])) == "<class 'hexbytes.main.HexBytes'>" else item[1]))
    print("========== Router exec fun: addLiquidityETH(Seacoin-ETH) {} End ==========\n".format( "Sucess!!!" if router_tx.status else "Failed!!!"))
    assert router_tx.status, "Router exec addLiquidityETH Failed!!!"


    print("========== Coin Info&Reserve Begin ==========")

    print("factory:{} feeToSetter:{}".format(factory_contract_tx.contractAddress, factory_attached_contract_obj.functions.feeToSetter().call()))

    seacoin_weth_pair_address = factory_attached_contract_obj.functions.getPair(seacoin_contract_tx.contractAddress, weth_contract_tx.contractAddress).call()
    print("seacoin_weth_pair_address:{}".format(seacoin_weth_pair_address))

    # token0 token1 token0_reserve token1_reserve
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(pair_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(pair) get some err:{}".format(errinfo))
        return
    pair_attached_contract_obj = w3.eth.contract(abi=abi, address=seacoin_weth_pair_address)

    token0 = pair_attached_contract_obj.functions.token0().call()
    token1 = pair_attached_contract_obj.functions.token1().call()
    token0_reserve, token1_reserve, blockTimestampLast = pair_attached_contract_obj.functions.getReserves().call()
    print("pair({}:{}) reserve({}:{})".format(token0, token1, token0_reserve, token1_reserve))


    # tocken0: name symbol decimals
    abi, bytecode, errinfo = get_abi_bytecode_from_contract_json_file(erc20_file)
    if errinfo:
        print("function get_abi_bytecode_from_contract_json_file(erc20) get some err:{}".format(errinfo))
        return
    token0_erc20_attached_contract_obj = w3.eth.contract(abi=abi, address=token0)
    token0_name = token0_erc20_attached_contract_obj.functions.name().call()
    token0_symbol = token0_erc20_attached_contract_obj.functions.symbol().call()
    token0_decimals = token0_erc20_attached_contract_obj.functions.decimals().call()
    print("{}:{} reserve:{} symbol:{} decimals:{}".format(token0_name, token0, token0_reserve, token0_symbol, token0_decimals))

    # tocken1: name symbol decimals
    token1_erc20_attached_contract_obj = w3.eth.contract(abi=abi, address=token1)
    token1_name = token1_erc20_attached_contract_obj.functions.name().call()
    token1_symbol = token1_erc20_attached_contract_obj.functions.symbol().call()
    token1_decimals = token1_erc20_attached_contract_obj.functions.decimals().call()
    print("{}:{} reserve:{} symbol:{} decimals:{}".format(token1_name, token1, token1_reserve, token1_symbol, token1_decimals))

    print("========== Coin Info&Reserve End ==========\n")



    print("========== Contracts Address Begin ==========")
    print("Factory:", factory_contract_tx.contractAddress)
    print("Router:", router_contract_tx.contractAddress)
    print("Weth:", weth_contract_tx.contractAddress)
    print("Seacoin:", seacoin_contract_tx.contractAddress)
    print("Pair seacoin-weth:", seacoin_weth_pair_address)
    print("========== Contracts Address End ==========")

if __name__ == "__main__":
    usage = "usage: python3 contractor.py [options] arg"
    parser = OptionParser(usage=usage, description="command descibe")
    parser.add_option("-g", "--gas", dest="tx_gas", type="int", default=8000000, help="tx gas, default 8000000")

    # group one click
    one_click_group = OptionGroup(parser=parser, title="One-Click-Deploy-Uniswap Program Options")
    one_click_group.add_option("-o", "--one_click", action='store_true', dest="one_click", default=False, help="one click deploy")
    one_click_group.add_option("-H", "--http", dest="geth_http", type="string", default="http://127.0.0.1:6060", help="geth http, default: http://127.0.0.1:6060")
    one_click_group.add_option("-1", "--weth", dest="weth_file", type="string", default="contracts/WETH9.json", help="weth contract, default: contracts/WETH9.json")
    one_click_group.add_option("-2", "--facory", dest="factory_file", type="string", default="contracts/UniswapV2Factory.json", help="factory contract default: contracts/UniswapV2Factory.json")
    one_click_group.add_option("-3", "--router", dest="router_file", type="string", default="contracts/UniswapV2Router02.json", help="router contract default: contracts/UniswapV2Router02.json")
    one_click_group.add_option("-4", "--seacoin", dest="seacoin_file", type="string", default="contracts/SeaCoin1.json", help="Seacoin contract default: contracts/SeaCoin1.json")
    one_click_group.add_option("-5", "--pair", dest="pair_file", type="string", default="contracts/UniswapV2Pair.json", help="pair contract default: contracts/UniswapV2Pair.json")
    one_click_group.add_option("-6", "--erc20", dest="erc20_file", type="string", default="contracts/ERC20.json", help="erc20 contract default: contracts/ERC20.json")
    parser.add_option_group(one_click_group)

    # group run contract
    run_contract_group = OptionGroup(parser=parser, title="Run-Contract Program Options")
    run_contract_group.add_option("-r", "--run", action='store_true', dest="run_contract", default=False, help="run contract")
    run_contract_group.add_option("-f", "--contract_file", dest="contract_file", type="string", help="contract json file")
    run_contract_group.add_option("-c", "--contract_address", dest="contract_address", type="string", default=None, help="contract address")
    parser.add_option_group(run_contract_group)

    (options, args) = parser.parse_args()

    if options.one_click:
        one_click_deploy(options.geth_http, options.weth_file, options.factory_file, options.router_file, options.seacoin_file, options.pair_file, options.erc20_file, options.tx_gas)
    elif options.run_contract:
        attach_contract(options.geth_http, options.contract_file, options.contract_address, options.tx_gas)
    else:
        parser.print_help()
