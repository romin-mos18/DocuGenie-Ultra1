'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
} from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibleDropdownProps {
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
  label: string;
  required?: boolean;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

export default function AccessibleDropdown({
  options,
  value,
  onChange,
  label,
  required = false,
  disabled = false,
  error = false,
  helperText,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
}: AccessibleDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);
  const { announceLoading, handleKeyDown } = useAccessibility();

  const handleChange = (event: any) => {
    const newValue = event.target.value;
    onChange(newValue);
    announceLoading(`Selected ${options.find(opt => opt.value === newValue)?.label || newValue}`);
  };

  const handleKeyDownEvent = (event: React.KeyboardEvent) => {
    handleKeyDown(event, {
      onEscape: () => setIsOpen(false),
    });
  };

  useEffect(() => {
    if (isOpen) {
      announceLoading(`${label} dropdown opened with ${options.length} options`);
    }
  }, [isOpen, label, options.length, announceLoading]);

  const selectAriaProps = {
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedBy,
    'aria-invalid': error ? true : false,
    'aria-required': required,
  };

  return (
    <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth error={error} disabled={disabled}>
        <InputLabel id={`${label}-label`}>{label}</InputLabel>
        <Select
          ref={selectRef}
          labelId={`${label}-label`}
          value={value}
          label={label}
          onChange={handleChange}
          onOpen={() => setIsOpen(true)}
          onClose={() => setIsOpen(false)}
          onKeyDown={handleKeyDownEvent}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-labelledby={`${label}-label`}
          {...selectAriaProps}
        >
          {options.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {helperText && (
        <Box
          component="div"
          id={`${label}-help`}
          sx={{
            fontSize: '0.75rem',
            color: error ? 'error.main' : 'text.secondary',
            mt: 0.5,
          }}
          role="status"
          aria-live="polite"
        >
          {helperText}
        </Box>
      )}
    </Box>
  );
}
