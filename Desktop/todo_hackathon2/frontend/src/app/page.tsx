import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

/**
 * Landing Page - Phase II Todo Hackathon
 * Redirects authenticated users to dashboard, others to login
 */
export default async function Home() {
  // Check for auth token in cookies/localStorage
  // Since we can't access localStorage in server components,
  // we'll rely on middleware to handle redirects
  // This page acts as a fallback that redirects to login
  redirect('/login');
}
