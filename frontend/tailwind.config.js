/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,jsx}"],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // Custom palette: #00072D → #001C55 → #0A2472 → #0E6BA8 → #A6E1FA
                primary: {
                    50: '#e6f5fe',
                    100: '#c2e6fc',
                    200: '#A6E1FA',   // lightest from palette
                    300: '#6dcbf5',
                    400: '#34a8e0',
                    500: '#0E6BA8',   // vivid blue from palette
                    600: '#0b5a8e',
                    700: '#0A2472',   // deep blue from palette
                    800: '#001C55',   // dark navy from palette
                    900: '#00072D',   // deepest from palette
                },
                accent: {
                    50: '#f0f9ff', 100: '#e0f2fe', 200: '#bae6fd', 300: '#7dd3fc',
                    400: '#38bdf8', 500: '#A6E1FA', 600: '#0E6BA8', 700: '#0A2472',
                    800: '#001C55', 900: '#00072D',
                },
                dark: {
                    50: '#f9fafb',
                    100: '#f3f4f6',
                    200: '#e5e7eb',
                    300: '#d1d5db',
                    400: '#9ca3af',
                    500: '#6b7280',
                    600: '#4b5563',
                    700: '#374151',
                    800: '#1f2937',
                    900: '#111827', // true gray/black
                    950: '#000000', // true black
                },
            },
            fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
            },
            keyframes: {
                fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
                slideUp: { '0%': { opacity: '0', transform: 'translateY(20px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
            },
        },
    },
    plugins: [],
}
