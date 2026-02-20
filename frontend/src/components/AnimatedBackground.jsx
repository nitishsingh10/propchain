import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// Import new photorealistic assets
import skyscraperImg from '../assets/bg_skyscraper.png'
import villaImg from '../assets/bg_villa.png'
// Keeping abstract as a backup or third option if needed, or replace with another realistic one later
import abstractImg from '../assets/bg_abstract.png'

const backgrounds = [
    {
        id: 1,
        src: skyscraperImg,
        alt: "Modern Skyscraper at Night"
    },
    {
        id: 2,
        src: villaImg,
        alt: "Luxury Villa Twilight"
    }
]

export default function AnimatedBackground() {
    const [index, setIndex] = useState(0)

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev + 1) % backgrounds.length)
        }, 8000) // 8 seconds per slide
        return () => clearInterval(timer)
    }, [])

    return (
        <div className="fixed inset-0 z-0 overflow-hidden bg-black">
            <AnimatePresence mode="popLayout" initial={false}>
                <motion.img
                    key={backgrounds[index].id}
                    src={backgrounds[index].src}
                    alt={backgrounds[index].alt}
                    initial={{ opacity: 0, scale: 1.1 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="w-full h-full object-cover opacity-60"
                />
            </AnimatePresence >

            {/* Heavy overlay for text readability */}
            < div className="absolute inset-0 bg-gradient-to-b from-dark-950/80 via-dark-900/60 to-dark-950/90 mix-blend-multiply" />
            <div className="absolute inset-0 bg-primary-900/20 mix-blend-overlay" />
            <div className="absolute inset-0 backdrop-blur-[1px]" />
        </div >
    )
}
