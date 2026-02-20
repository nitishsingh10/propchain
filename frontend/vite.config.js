import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
    plugins: [
        react(),
        nodePolyfills({
            include: ['buffer', 'crypto', 'stream', 'util', 'process'],
            globals: { Buffer: true, process: true },
        }),
    ],
    server: {
        port: 3000,
        host: true,
        cors: true,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
})
