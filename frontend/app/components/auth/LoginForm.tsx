'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Link as MuiLink,
  CircularProgress,
  Alert,
} from '@mui/material';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '../../store/store';
import { setUser, setToken } from '../../store/slices/authSlice';
import { getAriaDescribedBy, getAriaInvalid } from '../../../lib/accessibility';

interface LoginFormData {
  email: string;
  password: string;
}

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const dispatch = useAppDispatch();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const result = await response.json();

      // Update Redux store
      dispatch(setToken(result.token));
      dispatch(setUser(result.user));

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      component="main"
      id="main-content"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        minHeight: '100vh',
        pt: 8,
      }}
    >
      <Paper
        elevation={3}
        component="section"
        aria-labelledby="login-title"
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: 400,
          width: '100%',
        }}
      >
        <Typography 
          component="h1" 
          variant="h5" 
          gutterBottom
          id="login-title"
        >
          Sign In
        </Typography>

        {error && (
          <Alert 
            severity="error" 
            sx={{ width: '100%', mb: 2 }}
            role="alert"
            aria-live="assertive"
          >
            {error}
          </Alert>
        )}

        <Box 
          component="form" 
          onSubmit={handleSubmit(onSubmit)} 
          sx={{ width: '100%' }}
          noValidate
          aria-describedby={error ? 'error-message' : undefined}
        >
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            autoComplete="email"
            autoFocus
            error={!!errors.email}
            helperText={errors.email?.message}
            aria-describedby={getAriaDescribedBy(
              errors.email ? 'email-error' : undefined,
              'email-help'
            )}
            aria-invalid={getAriaInvalid(!!errors.email)}
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address',
              },
            })}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            id="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            error={!!errors.password}
            helperText={errors.password?.message}
            aria-describedby={getAriaDescribedBy(
              errors.password ? 'password-error' : undefined,
              'password-help'
            )}
            aria-invalid={getAriaInvalid(!!errors.password)}
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
            })}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
            aria-describedby={isLoading ? 'loading-status' : undefined}
          >
            {isLoading ? (
              <>
                <CircularProgress size={24} aria-hidden="true" />
                <span id="loading-status" className="sr-only">Loading...</span>
              </>
            ) : (
              'Sign In'
            )}
          </Button>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2">
              Don't have an account?{' '}
              <MuiLink component={Link} href="/register">
                Sign Up
              </MuiLink>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
