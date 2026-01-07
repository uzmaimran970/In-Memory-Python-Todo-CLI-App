import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware - Phase II Todo Hackathon
 * Handles route protection and authentication-based redirects
 *
 * Note: Since we're using localStorage for token storage (client-side only),
 * this middleware primarily handles route-level redirects. The actual auth
 * validation happens in client components via API calls.
 */

// Routes that require authentication
const protectedRoutes = ['/dashboard'];

// Routes that should redirect to dashboard if already authenticated
const authRoutes = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if it's a protected route
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  // Check if it's an auth route (login/signup)
  const isAuthRoute = authRoutes.some(route =>
    pathname.startsWith(route)
  );

  // Since localStorage is client-side only, we can't check auth token here
  // The middleware serves as a first-level guard, but actual auth validation
  // happens in components via API calls

  // For protected routes, let the page component handle auth checks
  // It will redirect to login if no valid token is found
  if (isProtectedRoute) {
    // Allow the request to proceed - the page component will validate
    return NextResponse.next();
  }

  // For auth routes (login/signup), allow access
  // If user is already authenticated, the component will redirect to dashboard
  if (isAuthRoute) {
    return NextResponse.next();
  }

  // For all other routes, continue normally
  return NextResponse.next();
}

// Configure which routes should be processed by this middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
