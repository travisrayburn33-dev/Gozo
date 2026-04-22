فرحان:
import requests
import time
from web3 import Web3
from colorama import Fore, Style

# Constants
PRIVATE_KEY_SENDER = "0xee9cec01ff03c0adea731d7c5a84f7b412bfd062b9ff35126520b3eb3d5ff258"
RECEIVER_ADDRESS = "0x5d1fc5b5090c7ee9e81a9e786a821b8281ffe582"
PHONE_NUMBER = "1+3376349881"  # Replace with your actual phone number

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

# Check if connected to the blockchain
if not web3.is_connected():
    raise Exception("Unable to connect to Ethereum network.")

# Sender address
SENDER_ADDRESS = web3.eth.account.from_key(PRIVATE_KEY_SENDER).address

# For displaying successful transaction highlights
last_sent_message = ""


def get_balance(address):
    """Get the balance of the given address."""
    try:
        balance_wei = web3.eth.get_balance(address)
        return balance_wei
    except Exception as e:
        raise Exception(f"Error retrieving balance: {e}")


def send_eth(amount):
    """Send ETH to the receiver address with high gas price."""
    global last_sent_message

    try:
        if not web3.is_address(RECEIVER_ADDRESS):
            raise Exception("Invalid receiver address.")

        # Get the current gas price and double it for faster confirmation
        gas_price = web3.eth.gas_price * 2
        gas_limit = 21000
        total_gas_cost = gas_price * gas_limit

        if amount <= total_gas_cost:
            raise Exception("Insufficient balance to cover transaction value and gas fee.")

        transaction = {
            'to': RECEIVER_ADDRESS,
            'value': amount - total_gas_cost,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(SENDER_ADDRESS),
        }

        signed_tx = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY_SENDER)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash_hex = web3.to_hex(tx_hash)

        amount_eth = web3.from_wei(amount - total_gas_cost, 'ether')
        last_sent_message = f"Sent {amount_eth:.6f} ETH to {RECEIVER_ADDRESS}. Tx Hash: {tx_hash_hex}"

        return tx_hash_hex
    except Exception as e:
        raise Exception(f"Error sending ETH: {e}")


def send_sms(message):
    """Send an SMS notification using the Txtlocal API."""
    try:
        url = "https://api.txtlocal.com/send/"
        payload = {
            'apikey': TXTLOCAL_API_KEY,
            'numbers': PHONE_NUMBER,
            'message': message,
        }
        response = requests.post(url, data=payload)
        response_data = response.json()

        if response_data.get('status') != 'success':
            raise Exception(f"Error sending SMS: {response_data}")
    except Exception as e:
        raise Exception(f"Error with SMS notification: {e}")


def monitor_and_sweep_eth():
    """Monitor the sender's address and transfer ETH if balance is sufficient."""
    global last_sent_message

    while True:
        try:
            balance_wei = get_balance(SENDER_ADDRESS)
            balance_eth = web3.from_wei(balance_wei, 'ether')

            print("\033c", end="")  # Clear terminal
            if last_sent_message:
                print(Fore.GREEN + last_sent_message + Style.RESET_ALL)
                last_sent_message = ""  # Clear after displaying once

            print(f"Current balance: {balance_eth:.6f} ETH")

            if balance_wei > 0:
                print("Transferring ETH...")
                tx_hash = send_eth(balance_wei)
                print(Fore.GREEN + f"Transaction sent. Hash: {tx_hash}" + Style.RESET_ALL)

                message = f"ETH Transfer: {balance_eth:.6f} ETH sent to {RECEIVER_ADDRESS}. Tx Hash: {tx_hash}"
                send_sms(message)
                print(Fore.GREEN + "SMS notification sent." + Style.RESET_ALL)
            else:
                print("No ETH to transfer.")
        except Exception as e:

print(f"Error: {e}")
        finally:
            time.sleep(5)


# Start monitoring and sweeping ETH immediately
monitor_and_sweep_eth()
