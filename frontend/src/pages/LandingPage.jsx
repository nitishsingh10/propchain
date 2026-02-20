import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Shield, TrendingUp, Users, Activity } from 'lucide-react'
import AnimatedBackground from '../components/AnimatedBackground'
import bgSkyscraper from '../assets/bg_skyscraper.png'
import bgVilla from '../assets/bg_villa.png'
import bgAbstract from '../assets/bg_abstract.png'

const STATS = [
    { label: 'Total Value Locked', target: 300, suffix: 'Cr+' },
    { label: 'Properties Listed', target: 42, suffix: '+' },
    { label: 'Active Investors', target: 1200, suffix: '+' },
    { label: 'Avg. Yield', target: 8.5, suffix: '%', decimals: 1 },
]

const FEATURES = [
    { icon: Shield, title: 'AI-Verified Properties', desc: 'Every property undergoes rigorous AI verification — documents, encumbrances, and ownership are analyzed automatically.' },
    { icon: Users, title: 'Fractional Ownership', desc: 'Own a piece of premium real estate for as little as ₹5,000. Buy shares like stocks and trade anytime.' },
    { icon: Activity, title: 'On-Chain Governance', desc: 'Vote on property decisions — sell, renovate, or change rent. Your shares, your voice.' },
    { icon: TrendingUp, title: 'Automated Rent Claims', desc: 'Rental income is distributed proportionally to share holders. Claim your earnings directly.' },
]

const HOW_IT_WORKS = [
    { step: '01', title: 'Connect Wallet', desc: 'Link your Pera Wallet to the Algorand Testnet' },
    { step: '02', title: 'Browse Properties', desc: 'Discover AI-verified real estate investments' },
    { step: '03', title: 'Buy Shares', desc: 'Purchase fractional shares with Algo tokens' },
    { step: '04', title: 'Earn Returns', desc: 'Receive rental income and governance rights' },
]

function AnimatedCounter({ target, suffix, decimals = 0 }) {
    const [count, setCount] = useState(0)
    const ref = useRef(null)
    const animated = useRef(false)

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !animated.current) {
                    animated.current = true
                    const duration = 1500
                    const startTime = Date.now()
                    const tick = () => {
                        const elapsed = Date.now() - startTime
                        const progress = Math.min(elapsed / duration, 1)
                        const eased = 1 - Math.pow(1 - progress, 3)
                        setCount(target * eased)
                        if (progress < 1) requestAnimationFrame(tick)
                    }
                    tick()
                }
            },
            { threshold: 0.3 }
        )
        if (ref.current) observer.observe(ref.current)
        return () => observer.disconnect()
    }, [target])

    return (
        <span ref={ref}>
            {decimals > 0 ? count.toFixed(decimals) : Math.floor(count)}
            {suffix}
        </span>
    )
}

export default function LandingPage() {
    const images = [bgSkyscraper, bgVilla, bgAbstract];

    return (
        <div className="relative min-h-screen font-sans text-white overflow-hidden">
            {/* Dynamic Background */}
            <AnimatedBackground images={images} />

            {/* Hero */}
            <section className="relative min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 text-center z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-primary-500/30 mb-8 backdrop-blur-md"
                >
                    <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                    <span className="text-secondary-100 text-sm font-medium tracking-wide">
                        LIVE ON ALGORAND TESTNET
                    </span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="text-5xl md:text-7xl font-bold mb-6 tracking-tight leading-tight drop-shadow-2xl"
                >
                    Own Real Estate <br />
                    <span className="gradient-text">One Share at a Time</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="text-xl text-gray-200 max-w-2xl mx-auto mb-10 leading-relaxed font-light drop-shadow-md"
                >
                    PropChain brings AI-verified property tokenization to Algorand.
                    Invest in premium real estate starting from ₹5,000 with full legal compliance.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="flex flex-col sm:flex-row gap-4 justify-center w-full"
                >
                    <Link to="/marketplace" className="btn-primary flex items-center justify-center gap-2 px-8 py-4 text-lg shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 transition-all transform hover:-translate-y-1">
                        Explore Properties <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link to="/list" className="px-8 py-4 rounded-xl glass-card border border-white/10 hover:bg-white/10 transition-all text-lg font-medium flex items-center justify-center backdrop-blur-md hover:backdrop-blur-lg">
                        List Your Property
                    </Link>
                </motion.div>

                {/* Floating Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.8 }}
                    className="mt-24 w-full max-w-5xl grid grid-cols-2 md:grid-cols-4 gap-4"
                >
                    {STATS.map((s, i) => (
                        <div key={s.label} className="glass-card p-6 rounded-2xl text-center border border-white/5 hover:border-white/20 transition-colors bg-dark-900/40 backdrop-blur-xl">
                            <div className="text-3xl font-bold text-white mb-1 drop-shadow-sm">
                                <AnimatedCounter target={s.target} suffix={s.suffix} decimals={s.decimals} />
                            </div>
                            <div className="text-sm text-gray-300 font-medium tracking-wide uppercase">{s.label}</div>
                        </div>
                    ))}
                </motion.div>
            </section>

            {/* Features */}
            <section className="relative z-10 py-24 px-4 max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl font-bold mb-4"
                    >
                        Why <span className="gradient-text">PropChain</span>?
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-gray-400 text-lg"
                    >
                        Built for the future of real estate investment
                    </motion.p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {FEATURES.map((f, i) => (
                        <motion.div
                            key={f.title}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="glass-card p-8 rounded-2xl border border-white/5 hover:border-primary-500/30 transition-all hover:bg-dark-900/60 group"
                        >
                            <h3 className="text-xl font-bold mb-3 text-white/90">{f.title}</h3>
                            <p className="text-gray-400 leading-relaxed text-sm">{f.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* How It Works */}
            <section className="relative z-10 py-20 px-4 max-w-5xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold mb-4">How It <span className="gradient-text">Works</span></h2>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {HOW_IT_WORKS.map((s, i) => (
                        <motion.div
                            key={s.step}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="glass-card p-6 text-center hover:bg-white/[0.06] transition-all rounded-xl border border-white/5"
                        >
                            <div className="text-3xl font-bold text-primary-400 mb-4 font-mono">{s.step}</div>
                            <h3 className="font-semibold text-lg mb-2">{s.title}</h3>
                            <p className="text-sm text-gray-400">{s.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="relative z-10 py-24 px-4">
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="max-w-4xl mx-auto glass-card p-12 rounded-3xl text-center relative overflow-hidden border-primary-500/20"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-500/[0.1] to-transparent" />
                    <div className="relative z-10">
                        <h2 className="text-4xl font-bold mb-6">Ready to Invest in <span className="gradient-text">Real Estate</span>?</h2>
                        <p className="text-gray-300 mb-10 max-w-lg mx-auto text-lg leading-relaxed">
                            Join thousands of investors building wealth through fractional property ownership on the blockchain.
                        </p>
                        <Link to="/marketplace" className="btn-primary text-lg px-10 py-4 shadow-xl shadow-primary-500/20">
                            Get Started Now
                        </Link>
                    </div>
                </motion.div>
            </section>
        </div>
    )
}
