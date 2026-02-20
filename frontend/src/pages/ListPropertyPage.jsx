import { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { WalletContext } from '../App'
import { useToast } from '../components/Toast'
import { LocationPickerMap, AddressAutocomplete } from '../components/PropertyMap'
import { api } from '../utils/api'
import { Upload, DollarSign, Building, MapPin, PieChart, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react'

export default function ListPropertyPage() {
    const { walletAddress } = useContext(WalletContext)
    const navigate = useNavigate()
    const toast = useToast()

    const [isLoading, setIsLoading] = useState(false)
    const [step, setStep] = useState(1) // 1: Details, 2: Documents, 3: Success
    const [propertyId, setPropertyId] = useState(null)

    const [formData, setFormData] = useState({
        propertyName: '',
        location: '',
        valuation: '',
        totalShares: '',
        minInvestment: '',
        maxInvestment: '',
    })

    const [files, setFiles] = useState([])
    const [mapLatLng, setMapLatLng] = useState(null)

    const calculateSharePrice = () => {
        if (!formData.valuation || !formData.totalShares) return 0
        return (parseInt(formData.valuation) / parseInt(formData.totalShares)).toFixed(2)
    }

    const handleInputChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files))
        }
    }

    const handleSubmitDetails = async (e) => {
        e.preventDefault()
        if (!walletAddress) {
            toast.error('Please connect your wallet first')
            return
        }

        setIsLoading(true)
        try {
            const sharePrice = Math.floor(parseInt(formData.valuation) / parseInt(formData.totalShares))

            const payload = {
                owner_address: walletAddress,
                property_name: formData.propertyName,
                location_hash: formData.location,
                valuation: parseInt(formData.valuation),
                total_shares: parseInt(formData.totalShares),
                share_price: sharePrice,
                min_investment: parseInt(formData.minInvestment),
                max_investment: parseInt(formData.maxInvestment)
            }

            const data = await api.submitProperty(payload)

            setPropertyId(data.property_id)
            setStep(2)
            toast.success('Property details submitted successfully')
        } catch (error) {
            console.error('Submission error:', error)
            toast.error(error.message)
        } finally {
            setIsLoading(false)
        }
    }

    const handleUploadDocuments = async () => {
        if (files.length === 0) {
            toast.error('Please select at least one document')
            return
        }

        setIsLoading(true)
        try {
            await api.verifyProperty(propertyId, files)

            setStep(3)
            toast.success('Documents uploaded and verification started')
        } catch (error) {
            console.error('Upload error:', error)
            toast.error(error.message)
        } finally {
            setIsLoading(false)
        }
    }

    if (!walletAddress) {
        return (
            <div className="min-h-screen pt-24 pb-12 px-4 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-2xl bg-white/[0.05] flex items-center justify-center mb-6">
                    <Building className="text-white/40" size={32} />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Connect Wallet to List</h2>
                <p className="text-white/50 max-w-md mb-8">
                    You need to connect your Algorand wallet to submit property details and upload legal documents for verification.
                </p>
            </div>
        )
    }

    return (
        <div className="min-h-screen pt-24 pb-20 px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="mb-10 text-center">
                    <h1 className="text-3xl font-bold text-white mb-3">List Your Property</h1>
                    <p className="text-white/50">Fractionalize your real estate and raise capital on Algorand.</p>
                </div>

                {/* Steps */}
                <div className="flex items-center justify-center mb-12">
                    <div className={`flex items-center gap-2 ${step >= 1 ? 'text-primary-400' : 'text-white/20'}`}>
                        <span className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center font-bold text-sm">1</span>
                        <span className="font-medium text-sm">Details</span>
                    </div>
                    <div className={`w-12 h-0.5 mx-4 ${step >= 2 ? 'bg-primary-500' : 'bg-white/10'}`} />
                    <div className={`flex items-center gap-2 ${step >= 2 ? 'text-primary-400' : 'text-white/20'}`}>
                        <span className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center font-bold text-sm">2</span>
                        <span className="font-medium text-sm">Documents</span>
                    </div>
                    <div className={`w-12 h-0.5 mx-4 ${step >= 3 ? 'bg-primary-500' : 'bg-white/10'}`} />
                    <div className={`flex items-center gap-2 ${step >= 3 ? 'text-primary-400' : 'text-white/20'}`}>
                        <span className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center font-bold text-sm">3</span>
                        <span className="font-medium text-sm">Finish</span>
                    </div>
                </div>

                {/* Content */}
                <div className="bg-white/[0.02] border border-white/[0.05] rounded-2xl p-6 sm:p-10 backdrop-blur-sm">
                    {step === 1 && (
                        <form onSubmit={handleSubmitDetails} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2 md:col-span-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Property Name</label>
                                    <div className="relative">
                                        <Building className="absolute left-3.5 top-3.5 text-white/30" size={18} />
                                        <input
                                            type="text"
                                            name="propertyName"
                                            value={formData.propertyName}
                                            onChange={handleInputChange}
                                            required
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 pl-10 pr-4 text-white placeholder-white/20 transition-all outline-none"
                                            placeholder="e.g. Sunset Villa, Mumbai"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2 md:col-span-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Location / Address</label>
                                    <div className="relative">
                                        <MapPin className="absolute left-3.5 top-3.5 text-white/30 z-10" size={18} />
                                        <AddressAutocomplete
                                            value={formData.location}
                                            onChange={(val) => setFormData(prev => ({ ...prev, location: val }))}
                                            onSelect={(address, lat, lng) => {
                                                setFormData(prev => ({ ...prev, location: address }))
                                                setMapLatLng([lat, lng])
                                            }}
                                            placeholder="Search for property address..."
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 pl-10 pr-4 text-white placeholder-white/20 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div className="md:col-span-2">
                                    <LocationPickerMap
                                        latLng={mapLatLng}
                                        onMapPinChange={(address, lat, lng) => {
                                            if (address) setFormData(prev => ({ ...prev, location: address }))
                                            setMapLatLng([lat, lng])
                                        }}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Valuation (INR)</label>
                                    <div className="relative">
                                        <span className="absolute left-3.5 top-3.5 text-white/30 font-bold">₹</span>
                                        <input
                                            type="number"
                                            name="valuation"
                                            value={formData.valuation}
                                            onChange={handleInputChange}
                                            required
                                            min="1000"
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 pl-10 pr-4 text-white placeholder-white/20 transition-all outline-none"
                                            placeholder="50,00,000"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Total Shares</label>
                                    <div className="relative">
                                        <PieChart className="absolute left-3.5 top-3.5 text-white/30" size={18} />
                                        <input
                                            type="number"
                                            name="totalShares"
                                            value={formData.totalShares}
                                            onChange={handleInputChange}
                                            required
                                            min="10"
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 pl-10 pr-4 text-white placeholder-white/20 transition-all outline-none"
                                            placeholder="5000"
                                        />
                                    </div>
                                </div>

                                <div className="md:col-span-2 p-4 bg-primary-500/10 border border-primary-500/20 rounded-xl flex items-center justify-between">
                                    <span className="text-sm text-primary-200">Estimated Price Per Share</span>
                                    <span className="text-lg font-bold text-white">₹ {calculateSharePrice()}</span>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Min Investment (Shares)</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            name="minInvestment"
                                            value={formData.minInvestment}
                                            onChange={handleInputChange}
                                            required
                                            min="1"
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 px-4 text-white placeholder-white/20 transition-all outline-none"
                                            placeholder="1"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Max Investment (Shares)</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            name="maxInvestment"
                                            value={formData.maxInvestment}
                                            onChange={handleInputChange}
                                            required
                                            min="1"
                                            className="w-full bg-black/20 border border-white/[0.08] hover:border-white/20 focus:border-primary-500 rounded-xl py-3 px-4 text-white placeholder-white/20 transition-all outline-none"
                                            placeholder="1000"
                                        />
                                    </div>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full mt-6 btn-primary py-4 text-base flex items-center justify-center gap-2 group"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : (
                                    <>
                                        Continue to Documents
                                        <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </button>
                        </form>
                    )}

                    {step === 2 && (
                        <div className="space-y-8">
                            <div className="text-center">
                                <h3 className="text-xl font-bold text-white">Upload Property Documents</h3>
                                <p className="text-white/50 text-sm mt-2">
                                    Please upload the Sale Deed, Encumbrance Certificate, and recent Tax Receipts.
                                    Our AI Oracle will verify these documents.
                                </p>
                            </div>

                            <div className="border-2 border-dashed border-white/10 hover:border-primary-500/50 rounded-2xl p-10 transition-colors text-center group">
                                <input
                                    type="file"
                                    id="file-upload"
                                    className="hidden"
                                    multiple
                                    accept=".pdf,.jpg,.jpeg,.png"
                                    onChange={handleFileChange}
                                />
                                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-4">
                                    <div className="w-16 h-16 rounded-full bg-white/[0.03] group-hover:bg-primary-500/10 flex items-center justify-center transition-colors">
                                        <Upload className="text-white/40 group-hover:text-primary-400" size={32} />
                                    </div>
                                    <div>
                                        <span className="text-primary-400 font-medium">Click to upload</span>
                                        <span className="text-white/40"> or drag and drop</span>
                                    </div>
                                    <p className="text-xs text-white/30">PDF, PNG, JPG up to 10MB</p>
                                </label>
                            </div>

                            {files.length > 0 && (
                                <div className="space-y-2">
                                    <p className="text-xs text-white/40 uppercase font-medium">Selected Files</p>
                                    {files.map((file, idx) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/[0.05]">
                                            <span className="text-sm text-white/80">{file.name}</span>
                                            <span className="text-xs text-white/40">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <button
                                onClick={handleUploadDocuments}
                                disabled={isLoading || files.length === 0}
                                className="w-full btn-primary py-4 text-base flex items-center justify-center gap-2"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : 'Start Verification'}
                            </button>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="text-center py-10">
                            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                                <CheckCircle2 className="text-green-500" size={40} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-4">Submission Successful!</h2>
                            <p className="text-white/60 mb-8 max-w-md mx-auto">
                                Your property ID is <span className="text-white font-mono bg-white/10 px-2 py-0.5 rounded">#{propertyId}</span>.
                                The AI Oracle is currently analyzing your documents. This process usually takes 2-5 minutes.
                            </p>
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <button
                                    onClick={() => navigate('/portfolio')}
                                    className="btn-primary w-full sm:w-auto px-8"
                                >
                                    View Portfolio
                                </button>
                                <button
                                    onClick={() => navigate('/')}
                                    className="btn-secondary w-full sm:w-auto px-8"
                                >
                                    Back to Home
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
