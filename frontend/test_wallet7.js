import algosdk from 'algosdk';
const base64Txn = "hqNhbXRko2ZlZc0D6KNnZW6sdGVzdG5ldC12MS4wo3JjdsQg17M5yfledj8eEP4LrnwOC/nDuVRUdPhD5+23FMNugGmjc25kxCDXsznJ+V52Px4Q/guufA4L+cO5VFR0+EPn7bcUw26AaaR0eXBlo3BheQ==";
const bytes = Uint8Array.from(atob(base64Txn), c => c.charCodeAt(0));
try {
    const txn = algosdk.decodeUnsignedTransaction(bytes);
    console.log("Decoded successfully. Type:", txn.constructor.name);
    console.log("Amount:", txn.amount);
} catch(e) {
    console.error("Decode error", e);
}
