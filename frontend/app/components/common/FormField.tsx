'use client';

import React from 'react';
import { TextField, FormControl, FormHelperText, Box } from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface FormFieldProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

export default function FormField({
  label,
  name,
  value,
  onChange,
  error,
  helperText,
  required = false,
  disabled = false,
  type = 'text',
  placeholder,
  multiline = false,
  rows = 1,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
}: FormFieldProps) {
  const { getFormFieldAriaProps } = useAccessibility();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  const ariaProps = getFormFieldAriaProps({
    name,
    error,
    helperText,
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedBy,
  });

  return (
    <Box sx={{ mb: 2 }}>
      <FormControl fullWidth error={!!error} disabled={disabled}>
        <TextField
          label={label}
          name={name}
          value={value}
          onChange={handleChange}
          type={type}
          placeholder={placeholder}
          multiline={multiline}
          rows={rows}
          required={required}
          disabled={disabled}
          {...ariaProps}
        />
        {(error || helperText) && (
          <FormHelperText
            id={`${name}-help`}
            error={!!error}
            role="status"
            aria-live="polite"
          >
            {error || helperText}
          </FormHelperText>
        )}
      </FormControl>
    </Box>
  );
}
