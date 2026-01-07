'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { api, setAuthToken, validateEmail, validatePassword } from '@/lib';
import { toast } from '@/components/ui/Toast';

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Validation errors
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  // Real-time validation
  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (value.length > 0) {
      setEmailError(validateEmail(value));
    } else {
      setEmailError(null);
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (value.length > 0) {
      setPasswordError(validatePassword(value));
    } else {
      setPasswordError(null);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate all fields before submission
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    setEmailError(emailValidation);
    setPasswordError(passwordValidation);

    // Stop if any validation errors
    if (emailValidation || passwordValidation) {
      toast.error('Please fix the form errors before submitting');
      return;
    }

    setIsLoading(true);

    try {
      const loginData = {
        email: email.trim(),
        password,
      };

      console.log('[LOGIN] Sending login request...', { email: loginData.email, hasPassword: !!loginData.password });
      const response = await api.login(loginData);
      console.log('[LOGIN] API Response received:', {
        hasToken: !!response.token,
        tokenPreview: response.token ? `${response.token.substring(0, 30)}...` : 'NO TOKEN',
        tokenLength: response.token?.length,
        user: response.user,
        fullResponse: response
      });

      // Store JWT token
      console.log('[LOGIN] About to save token to localStorage...');
      setAuthToken(response.token);

      // Verify token was saved
      const savedToken = localStorage.getItem('auth_token');
      console.log('[LOGIN] Token saved. Verification:', savedToken ? 'SUCCESS' : 'FAILED');
      console.log('[LOGIN] Saved token preview:', savedToken ? `${savedToken.substring(0, 30)}...` : 'NO TOKEN');

      // Show success message
      toast.success(`Welcome back${response.user.name ? `, ${response.user.name}` : ''}!`);

      // Small delay to ensure localStorage persists before navigation
      console.log('[LOGIN] Waiting 100ms before redirect...');
      await new Promise(resolve => setTimeout(resolve, 100));

      console.log('[LOGIN] Redirecting to dashboard...');
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      // Handle API errors
      const errorMessage = error instanceof Error
        ? error.message
        : 'Login failed. Please check your credentials and try again.';

      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 md:space-y-6" noValidate>
      <Input
        type="email"
        label="Email"
        value={email}
        onChange={handleEmailChange}
        placeholder="you@example.com"
        error={emailError || undefined}
        required
        disabled={isLoading}
      />

      <Input
        type="password"
        label="Password"
        value={password}
        onChange={handlePasswordChange}
        placeholder="Enter your password"
        error={passwordError || undefined}
        required
        disabled={isLoading}
      />

      <Button
        type="submit"
        variant="primary"
        size="large"
        loading={isLoading}
        disabled={isLoading || !!emailError || !!passwordError}
        className="w-full"
      >
        {isLoading ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}
