import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Smart Job Scraper v2.0 | Find Your Dream Tech Job',
  description: 'Modern job scraper for cybersecurity and software engineering positions. Built with Next.js 14 and TypeScript.',
  keywords: ['job scraper', 'cybersecurity jobs', 'software engineering jobs', 'tech careers'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}