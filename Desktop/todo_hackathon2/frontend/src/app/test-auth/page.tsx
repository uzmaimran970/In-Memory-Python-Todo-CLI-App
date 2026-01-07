'use client';

import { useState } from 'react';

export default function TestAuthPage() {
  const [status, setStatus] = useState<string[]>(['Ready to test authentication...']);
  const [token, setToken] = useState<string>('');

  const addStatus = (msg: string) => {
    setStatus(prev => [...prev, msg]);
  };

  const testAuth = async () => {
    setStatus(['Starting authentication test...']);

    try {
      // Step 1: Clear localStorage
      localStorage.clear();
      addStatus('✓ Cleared localStorage');

      // Step 2: Login
      addStatus('Sending login request...');
      const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'backendtest@test.com',
          password: 'test123'
        })
      });

      if (!loginResponse.ok) {
        addStatus(`✗ Login failed: ${loginResponse.status} ${loginResponse.statusText}`);
        return;
      }

      const loginData = await loginResponse.json();
      addStatus(`✓ Login successful`);
      addStatus(`Token received: ${loginData.token ? loginData.token.substring(0, 30) + '...' : 'NO TOKEN'}`);

      if (!loginData.token) {
        addStatus('✗ ERROR: No token in response!');
        return;
      }

      // Step 3: Save to localStorage
      localStorage.setItem('auth_token', loginData.token);
      setToken(loginData.token);
      addStatus('✓ Token saved to localStorage');

      // Step 4: Verify it was saved
      const savedToken = localStorage.getItem('auth_token');
      if (savedToken === loginData.token) {
        addStatus('✓ Token verification: SUCCESS');
      } else {
        addStatus('✗ Token verification: FAILED');
        return;
      }

      // Step 5: Test API call with token
      addStatus('Testing /api/auth/me with token...');
      const meResponse = await fetch('http://localhost:8000/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${savedToken}`,
          'Content-Type': 'application/json'
        }
      });

      addStatus(`API Response: ${meResponse.status} ${meResponse.statusText}`);

      if (meResponse.ok) {
        const userData = await meResponse.json();
        addStatus(`✓ Authentication working! User: ${userData.email}`);
        addStatus('✓ ✓ ✓ ALL TESTS PASSED ✓ ✓ ✓');
      } else {
        addStatus(`✗ API call failed: ${meResponse.status}`);
        const errorText = await meResponse.text();
        addStatus(`Error: ${errorText}`);
      }

    } catch (error) {
      addStatus(`✗ Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const testLoginPage = () => {
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Authentication Test Page</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Direct Backend Test</h2>
          <p className="text-gray-600 mb-4">
            This will test authentication directly with the backend API
          </p>
          <button
            onClick={testAuth}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-medium"
          >
            Run Test
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Login Page</h2>
          <p className="text-gray-600 mb-4">
            Go to the actual login page to test the full flow
          </p>
          <button
            onClick={testLoginPage}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
          >
            Go to Login Page
          </button>
        </div>

        <div className="bg-gray-900 text-green-400 rounded-lg p-6 font-mono text-sm">
          <h3 className="text-white font-semibold mb-3">Test Results:</h3>
          <div className="space-y-1">
            {status.map((msg, idx) => (
              <div key={idx}>{msg}</div>
            ))}
          </div>
        </div>

        {token && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-6">
            <h3 className="font-semibold mb-2">Current Token:</h3>
            <div className="bg-gray-100 p-3 rounded text-xs break-all">
              {token}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
