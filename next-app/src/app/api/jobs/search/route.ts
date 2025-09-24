import { NextRequest, NextResponse } from 'next/server'

// Proxy to Python backend deployed on Railway/Render/VM.
// Set BACKEND_URL (or NEXT_PUBLIC_BACKEND_URL) in your frontend environment, e.g.:
// https://your-backend.up.railway.app

export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL
    if (!backendUrl) {
      return NextResponse.json({ success: false, error: 'BACKEND_URL is not set' }, { status: 500 })
    }

    const payload = await request.json()

    const res = await fetch(`${backendUrl.replace(/\/$/, '')}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      // Ensure the server function can reach external URL
      // (Next.js edge runtimes need explicit opts; default node runtime is fine)
    })

    const data = await res.json().catch(() => ({ success: false, error: 'Invalid JSON from backend' }))
    return NextResponse.json(data, { status: res.ok ? 200 : 500 })
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
