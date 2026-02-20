import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const ToastContext = createContext(null)

export function useToast() {
    const ctx = useContext(ToastContext)
    if (!ctx) throw new Error('useToast must be used within ToastProvider')
    return ctx
}

function ToastItem({ toast, onRemove }) {
    const [exiting, setExiting] = useState(false)

    useEffect(() => {
        const timer = setTimeout(() => {
            setExiting(true)
            setTimeout(onRemove, 300)
        }, toast.duration || 4000)
        return () => clearTimeout(timer)
    }, [toast.duration, onRemove])

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' }
    const colors = {
        success: 'border-primary-500/40 bg-primary-500/10',
        error: 'border-red-500/40 bg-red-500/10',
        info: 'border-accent-500/40 bg-accent-500/10',
        warning: 'border-yellow-500/40 bg-yellow-500/10',
    }

    return (
        <div className={`toast-item flex items-start gap-3 px-5 py-4 rounded-xl border backdrop-blur-xl shadow-2xl max-w-sm
            ${colors[toast.type] || colors.info} ${exiting ? 'toast-exit' : 'toast-enter'}`}>
            <span className="text-lg mt-0.5 shrink-0">{icons[toast.type] || icons.info}</span>
            <div className="flex-1 min-w-0">
                {toast.title && <div className="font-semibold text-sm mb-0.5">{toast.title}</div>}
                <div className="text-sm text-white/70">{toast.message}</div>
            </div>
            <button onClick={() => { setExiting(true); setTimeout(onRemove, 300) }}
                className="text-white/30 hover:text-white/60 text-lg shrink-0 leading-none">×</button>
        </div>
    )
}

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([])

    const addToast = useCallback((type, message, title = '', duration = 4000) => {
        const id = Date.now() + Math.random()
        setToasts(prev => [...prev, { id, type, message, title, duration }])
    }, [])

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }, [])

    const toast = {
        success: (msg, title) => addToast('success', msg, title),
        error: (msg, title) => addToast('error', msg, title),
        info: (msg, title) => addToast('info', msg, title),
        warning: (msg, title) => addToast('warning', msg, title),
    }

    return (
        <ToastContext.Provider value={toast}>
            {children}
            <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3">
                {toasts.map(t => (
                    <ToastItem key={t.id} toast={t} onRemove={() => removeToast(t.id)} />
                ))}
            </div>
        </ToastContext.Provider>
    )
}
