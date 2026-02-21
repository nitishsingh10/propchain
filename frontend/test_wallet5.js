import algosdk from 'algosdk';
const base64Txn = "gqNhbXTOATtMOKNmZWXNA+iiZnbNA+GjZ2Vuq3Rlc3RuZXQtdjEuMKNnaHDEIOLw/Lg91+rB4i3o95z5c3y6ZqFpC8a+4xR9vT1sItCjo2x2zQUro3JjdsQgjU0E/H1TnjqGzPmsXW0r+q99o8i7U3G98f2h7hL3hOSkbm90ZcQqUHJvcENoYWluOiBCdXkgMTAgc2hhcmVzIG9mIFByb3AgMaZzbmRlxCCNTQT8fVOeOobM+axdbSv6r32jyLtTcb3x/aHuEveE5KR0eXBlo3BheQ==";
const bytes = Uint8Array.from(atob(base64Txn), c => c.charCodeAt(0));
try {
    const txn = algosdk.decodeUnsignedTransaction(bytes);
    console.log("Decoded successfully. Type:", txn.constructor.name);
    console.log("Amount:", txn.amount);
} catch(e) {
    console.error("Decode error", e);
}
