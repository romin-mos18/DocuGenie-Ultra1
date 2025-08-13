'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Avatar,
  IconButton,
  Grid,
} from '@mui/material';
import { PhotoCamera } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/store/store';
import { setUser } from '@/store/slices/authSlice';

interface ProfileFormData {
  name: string;
  email: string;
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

export default function ProfileForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ProfileFormData>({
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
    },
  });

  const newPassword = watch('newPassword');

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      // TODO: Replace with actual API call
      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const result = await response.json();

      // Update Redux store
      dispatch(setUser(result.user));

      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setIsLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('avatar', file);

      // TODO: Replace with actual API call
      const response = await fetch('/api/users/avatar', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload avatar');
      }

      const result = await response.json();

      // Update Redux store
      dispatch(setUser(result.user));

      setSuccess('Avatar updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography component="h1" variant="h5" gutterBottom>
          Profile Settings
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <input
            accept="image/*"
            style={{ display: 'none' }}
            id="avatar-upload"
            type="file"
            onChange={handleAvatarUpload}
          />
          <label htmlFor="avatar-upload">
            <IconButton
              color="primary"
              aria-label="upload picture"
              component="span"
              sx={{ position: 'relative' }}
            >
              <Avatar
                sx={{ width: 100, height: 100, mb: 1 }}
                src={user?.avatar || undefined}
              />
              <PhotoCamera
                sx={{
                  position: 'absolute',
                  bottom: 8,
                  right: 8,
                  backgroundColor: 'background.paper',
                  borderRadius: '50%',
                  p: 0.5,
                }}
              />
            </IconButton>
          </label>
        </Box>

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="name"
                label="Full Name"
                autoComplete="name"
                error={!!errors.name}
                helperText={errors.name?.message}
                {...register('name', {
                  required: 'Name is required',
                  minLength: {
                    value: 2,
                    message: 'Name must be at least 2 characters',
                  },
                })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                id="email"
                label="Email Address"
                autoComplete="email"
                error={!!errors.email}
                helperText={errors.email?.message}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Change Password
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                id="currentPassword"
                label="Current Password"
                type="password"
                error={!!errors.currentPassword}
                helperText={errors.currentPassword?.message}
                {...register('currentPassword')}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                id="newPassword"
                label="New Password"
                type="password"
                error={!!errors.newPassword}
                helperText={errors.newPassword?.message}
                {...register('newPassword', {
                  minLength: {
                    value: 8,
                    message: 'Password must be at least 8 characters',
                  },
                  pattern: {
                    value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
                    message:
                      'Password must contain at least one uppercase letter, one lowercase letter, one number and one special character',
                  },
                })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                id="confirmPassword"
                label="Confirm New Password"
                type="password"
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                {...register('confirmPassword', {
                  validate: (value) =>
                    !newPassword || value === newPassword || 'Passwords do not match',
                })}
              />
            </Grid>
          </Grid>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
