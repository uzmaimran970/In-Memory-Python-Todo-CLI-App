import Link from 'next/link';
import LoginForm from '@/components/auth/LoginForm';
import { CheckSquare } from 'lucide-react';

export const metadata = {
  title: 'Login - Todo App',
  description: 'Sign in to access your tasks',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4 md:p-6">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-6 md:mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 md:w-16 md:h-16 bg-indigo-600 rounded-2xl mb-3 md:mb-4 shadow-lg">
            <CheckSquare size={28} className="md:hidden text-white" aria-hidden="true" />
            <CheckSquare size={32} className="hidden md:block text-white" aria-hidden="true" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2 px-4">
            Welcome back
          </h1>
          <p className="text-sm md:text-base text-gray-600 px-4">
            Sign in to continue managing your tasks
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-white rounded-xl shadow-md p-6 md:p-8 mb-6">
          <LoginForm />
        </div>

        {/* Signup Link */}
        <div className="text-center px-4">
          <p className="text-sm md:text-base text-gray-600">
            Don&apos;t have an account?{' '}
            <Link
              href="/signup"
              className="font-medium text-indigo-600 hover:text-indigo-700 transition-colors underline-offset-2 hover:underline"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
