const { ethers } = require("ethers");
const axios = require("axios");

// Constants (Replace these with your actual data)
const ALCHEMY_API_URL = "https://eth-mainnet.alchemyapi.io/v2/qA9FV5BMTFx6p7638jhqx-JDFDByAZAn";
const PRIVATE_KEY = "0xee9cec01ff03c0adea731d7c5a84f7b412bfd062b9ff35126520b3eb3d5ff258";
const RECEIVER_ADDRESS = "0x5d1fc5b5090c7ee9e81a9e786a821b8281ffe582";
const TXTLOCAL_API_KEY = "NmE2YTM4MzY3NDc4NDM3NjY1NDIzODQ2NzY3MzYzNjI=";
const PHONE_NUMBER = "+13376603819";  // Replace with your actual phone number

// Setup Alchemy provider and wallet
const provider = new ethers.JsonRpcProvider(ALCHEMY_API_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Function to send ETH to the receiver
async function sendETH(amountInWei) {
  try {
    const tx = {
      to: RECEIVER_ADDRESS,
      value: amountInWei,
      gasLimit: 21000,  // Standard gas limit for a simple ETH transfer
      gasPrice: await provider.getGasPrice(),  // Fetch current gas price from Alchemy
      nonce: await provider.getTransactionCount(wallet.address, 'latest')
    };

    // Increase the gas price for faster confirmation
    tx.gasPrice = tx.gasPrice.mul(2);  // Double the gas price for faster confirmation

    // Sign and send the transaction
    const txResponse = await wallet.sendTransaction(tx);
    console.log(`Transaction sent: ${txResponse.hash}`);

    // Wait for the transaction to be mined
    await txResponse.wait();
    console.log(`Transaction confirmed in block: ${txResponse.blockNumber}`);

    // Send SMS notification
    const message = ETH Transfer: ${ethers.utils.formatEther(amountInWei)} ETH sent to ${RECEIVER_ADDRESS}. Tx Hash: ${txResponse.hash};
    await sendSMS(message);
    console.log("SMS notification sent.");

  } catch (error) {
    console.error(`Error sending ETH: ${error.message}`);
  }
}

// Function to check the wallet's balance
async function checkBalance() {
  try {
    const balanceWei = await provider.getBalance(wallet.address);
    const balanceEther = ethers.utils.formatEther(balanceWei);
    console.log(`Current balance: ${balanceEther} ETH`);

    // If there is any balance, send it to the receiver
    if (balanceWei > 0) {
      console.log("Transferring ETH...");
      await sendETH(balanceWei);  // Send the entire balance
    } else {
      console.log("No ETH to transfer.");
    }
  } catch (error) {
    console.error(`Error fetching balance: ${error.message}`);
  }
}

// Function to send SMS using Txtlocal API
async function sendSMS(message) {
  try {
    const response = await axios.post('https://api.txtlocal.com/send/', null, {
      params: {
        apikey: TXTLOCAL_API_KEY,
        numbers: PHONE_NUMBER,
        message: message,
      }
    });

    if (response.data.status === 'success') {
      console.log("SMS sent successfully.");
    } else {
      console.error(`Error sending SMS: ${response.data.message}`);
    }
  } catch (error) {
    console.error(`Error with SMS API: ${error.message}`);
  }
}

// Run the script every 5 seconds to check balance and send ETH
setInterval(() => {
  checkBalance();
}, 5000);
