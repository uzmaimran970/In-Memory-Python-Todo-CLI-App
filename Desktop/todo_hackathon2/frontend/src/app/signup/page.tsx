import Link from 'next/link';
import SignupForm from '@/components/auth/SignupForm';
import { CheckSquare } from 'lucide-react';

export const metadata = {
  title: 'Sign Up - Todo App',
  description: 'Create your account to start managing your tasks',
};

export default function SignupPage() {
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
            Create your account
          </h1>
          <p className="text-sm md:text-base text-gray-600 px-4">
            Start organizing your tasks efficiently
          </p>
        </div>

        {/* Signup Form Card */}
        <div className="bg-white rounded-xl shadow-md p-6 md:p-8 mb-6">
          <SignupForm />
        </div>

        {/* Login Link */}
        <div className="text-center px-4">
          <p className="text-sm md:text-base text-gray-600">
            Already have an account?{' '}
            <Link
              href="/login"
              className="font-medium text-indigo-600 hover:text-indigo-700 transition-colors underline-offset-2 hover:underline"
            >
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
