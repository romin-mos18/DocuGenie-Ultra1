'use client';

import React from 'react';
import { Box, Button, Alert, Typography } from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibleFormProps {
  children: React.ReactNode;
  onSubmit: (e: React.FormEvent) => void;
  title?: string;
  description?: string;
  error?: string;
  success?: string;
  loading?: boolean;
  submitText?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

export default function AccessibleForm({
  children,
  onSubmit,
  title,
  description,
  error,
  success,
  loading = false,
  submitText = 'Submit',
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
}: AccessibleFormProps) {
  const { announceError, announceSuccess } = useAccessibility();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(e);
  };

  React.useEffect(() => {
    if (error) {
      announceError(error);
    }
  }, [error, announceError]);

  React.useEffect(() => {
    if (success) {
      announceSuccess(success);
    }
  }, [success, announceSuccess]);

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}
    >
      {title && (
        <Typography variant="h4" component="h1" gutterBottom>
          {title}
        </Typography>
      )}

      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {description}
        </Typography>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} role="alert" aria-live="assertive">
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} role="alert" aria-live="polite">
          {success}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        {children}
      </Box>

      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={loading}
        aria-describedby={loading ? 'loading-status' : undefined}
      >
        {loading ? 'Submitting...' : submitText}
      </Button>

      {loading && (
        <Typography
          id="loading-status"
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1, textAlign: 'center' }}
          role="status"
          aria-live="polite"
        >
          Please wait while we process your request...
        </Typography>
      )}
    </Box>
  );
}

// Helper component for form fields
interface FormFieldProps {
  children: React.ReactNode;
  hasError?: boolean;
  errorId?: string;
  helpId?: string;
  required?: boolean;
}

export function FormField({ children, hasError = false, errorId, helpId, required = false }: FormFieldProps) {
  const { getFormFieldAriaProps } = useAccessibility();
  
  const ariaProps = getFormFieldAriaProps({
    name: 'form-field',
    error: hasError ? 'Error' : undefined,
    helperText: helpId,
  });
  
  return (
    <Box
      sx={{
        position: 'relative',
        mb: 2,
      }}
      aria-required={required}
    >
      {children}
    </Box>
  );
}
