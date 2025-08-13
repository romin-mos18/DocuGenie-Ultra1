'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to dashboard
    router.push('/dashboard')
  }, [router])

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ color: '#1976d2', marginBottom: '20px' }}>DocuGenie Ultra</h1>
        <p>Redirecting to dashboard...</p>
      </div>
    </div>
  )
}