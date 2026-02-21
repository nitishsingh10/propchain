const algosdk = require('algosdk');
const DEV_MNEMONIC = "era lecture duck age shed science cage brown green school explain enough roast dirt judge feel scan give erosion kangaroo mean very tape abstract claim";
const { addr } = algosdk.mnemonicToSecretKey(DEV_MNEMONIC);
console.log("addr:", addr, "type:", typeof addr);
