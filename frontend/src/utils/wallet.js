/**
 * PropChain — Pera Wallet Integration
 */
import { PeraWalletConnect } from '@perawallet/connect'

const peraWallet = new PeraWalletConnect({ chainId: 416002 }) // Testnet

export async function connectWallet() {
    try {
        const accounts = await peraWallet.connect()
        peraWallet.connector?.on('disconnect', () => { console.log('Wallet disconnected') })
        return { address: accounts[0], connector: peraWallet }
    } catch (error) {
        if (error?.data?.type !== 'CONNECT_MODAL_CLOSED') {
            console.error('Wallet connection error:', error)
        }
        return null
    }
}

export async function disconnectWallet() {
    try { await peraWallet.disconnect() } catch (e) { console.error(e) }
}

// --- Local Developer Wallet (for testing on localhost) ---
import algosdk from 'algosdk'

const DEV_MNEMONIC = "era lecture duck age shed science cage brown green school explain enough roast dirt judge feel scan give erosion kangaroo mean very tape abstract claim"

class DevWallet {
    constructor() {
        this.account = null
    }

    async connect() {
        try {
            const { addr, sk } = algosdk.mnemonicToSecretKey(DEV_MNEMONIC)
            // addr is an object (PublicKey), we need string for UI
            const addrStr = addr.toString()
            this.account = { addr: addrStr, sk }
            console.log("Dev Wallet connected:", addrStr)
            return [addrStr]
        } catch (e) {
            console.error("Dev Wallet error:", e)
            return []
        }
    }

    async signTransaction(txns) {
        if (!this.account) throw new Error("Dev Wallet not connected")

        // Pera Connect API expects an array of arrays of objects { txn: ... }
        // We need to unpack that structure, sign, and return blobs
        // Warning: minimal implementation for demo purposes
        const signedTxns = []

        for (const group of txns) {
            for (const wrapper of group) {
                // wrapper.txn is likely the logicSig or Transaction object
                // If it's a raw object, we might need to cast it.
                // Assuming standard algosdk Transaction object here.
                if (wrapper.signers && wrapper.signers.length === 0) {
                    continue // LogicSig or similar, skip signing
                }
                const signed = wrapper.txn.signTxn(this.account.sk)
                signedTxns.push(signed)
            }
        }
        return signedTxns
    }
}

const devWallet = new DevWallet()

export async function connectDevWallet() {
    const accounts = await devWallet.connect()
    if (accounts.length > 0) {
        return { address: accounts[0], connector: devWallet, isDev: true }
    }
    return null
}

export async function signTransaction(connector, txn) {
    try {
        // If it's our DexWallet (duck typing or flag)
        if (connector instanceof DevWallet) {
            // Wrap single txn in Pera-like structure for compatibility if needed, 
            // but our DevWallet.signTransaction handles the array structure.
            // We need to match what the calling code passes.
            // Usually calling code passes `[[{ txn }]]` for Pera.
            return await connector.signTransaction([[{ txn }]])
        }

        // Standard Pera
        const signedTxn = await connector.signTransaction([[{ txn }]])
        return signedTxn
    } catch (error) {
        console.error('Transaction signing error:', error)
        return null
    }
}

export function truncateAddress(address) {
    if (!address) return ''
    return `${address.slice(0, 6)}...${address.slice(-4)}`
}
