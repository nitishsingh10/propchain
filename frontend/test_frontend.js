import algosdk from 'algosdk';

const base64 = "iqNhbXTNxj6jZmVlzQPoomZ2zgOe53ajZ2VurHRlc3RuZXQtdjEuMKJnaMQgSGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiKibHbOA57rXqRub3RlxCJQcm9wQ2hhaW46IEJ1eSAxMCBzaGFyZXMgb2YgUHJvcCAxo3JjdsQg17M5yfledj8eEP4LrnwOC/nDuVRUdPhD5+23FMNugGmjc25kxCDXsznJ+V52Px4Q/guufA4L+cO5VFR0+EPn7bcUw26AaaR0eXBlo3BheQ==";

const base64ToUint8Array = (base64) => {
    const padding = '='.repeat((4 - base64.length % 4) % 4);
    const base64Standard = (base64 + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const binaryString = atob(base64Standard)
    const len = binaryString.length
    const bytes = new Uint8Array(len)
    for (let i = 0; i < len; i++) { bytes[i] = binaryString.charCodeAt(i) }
    return bytes
}

try {
    const txnArray = base64ToUint8Array(base64);
    const decodedTxn = algosdk.decodeUnsignedTransaction(txnArray);
    console.log("Decoded amount:", decodedTxn.amount);
} catch (e) {
    console.error("Error:", e);
}
