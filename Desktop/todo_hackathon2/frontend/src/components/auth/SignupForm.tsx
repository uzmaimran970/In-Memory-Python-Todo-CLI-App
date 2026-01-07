'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { api, setAuthToken, validateEmail, validatePassword, validateName } from '@/lib';
import { toast } from '@/components/ui/Toast';

export default function SignupForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Validation errors
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);

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

  const handleNameChange = (value: string) => {
    setName(value);
    setNameError(validateName(value));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate all fields before submission
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);
    const nameValidation = validateName(name);

    setEmailError(emailValidation);
    setPasswordError(passwordValidation);
    setNameError(nameValidation);

    // Stop if any validation errors
    if (emailValidation || passwordValidation || nameValidation) {
      toast.error('Please fix the form errors before submitting');
      return;
    }

    setIsLoading(true);

    try {
      const signupData = {
        email: email.trim(),
        password,
        ...(name.trim() && { name: name.trim() }),
      };

      console.log('[SIGNUP] Sending signup request...', { email: signupData.email, hasPassword: !!signupData.password });
      const response = await api.signup(signupData);
      console.log('[SIGNUP] API Response received:', {
        hasToken: !!response.token,
        tokenPreview: response.token ? `${response.token.substring(0, 30)}...` : 'NO TOKEN',
        tokenLength: response.token?.length,
        user: response.user
      });

      // Store JWT token
      console.log('[SIGNUP] About to save token to localStorage...');
      setAuthToken(response.token);

      // Verify token was saved
      const savedToken = localStorage.getItem('auth_token');
      console.log('[SIGNUP] Token saved. Verification:', savedToken ? 'SUCCESS' : 'FAILED');
      console.log('[SIGNUP] Saved token preview:', savedToken ? `${savedToken.substring(0, 30)}...` : 'NO TOKEN');

      // Show success message
      toast.success(`Welcome${response.user.name ? `, ${response.user.name}` : ''}! Your account has been created.`);

      // Small delay to ensure localStorage persists before navigation
      console.log('[SIGNUP] Waiting 100ms before redirect...');
      await new Promise(resolve => setTimeout(resolve, 100));

      console.log('[SIGNUP] Redirecting to dashboard...');
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      // Handle API errors
      const errorMessage = error instanceof Error
        ? error.message
        : 'Signup failed. Please try again.';

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
        placeholder="At least 8 characters"
        error={passwordError || undefined}
        helperText={!passwordError ? "Must be at least 8 characters long" : undefined}
        required
        disabled={isLoading}
      />

      <Input
        type="text"
        label="Name (optional)"
        value={name}
        onChange={handleNameChange}
        placeholder="Your name"
        error={nameError || undefined}
        disabled={isLoading}
        maxLength={100}
      />

      <Button
        type="submit"
        variant="primary"
        size="large"
        loading={isLoading}
        disabled={isLoading || !!emailError || !!passwordError || !!nameError}
        className="w-full"
      >
        {isLoading ? 'Creating account...' : 'Create account'}
      </Button>
    </form>
  );
}
