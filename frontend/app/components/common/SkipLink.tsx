'use client';

import React from 'react';
import { Box } from '@mui/material';
import { useSkipLink } from '../../../lib/accessibility';

export default function SkipLink() {
  const skipLinkRef = useSkipLink();

  return (
    <Box
      component="a"
      ref={skipLinkRef}
      href="#main-content"
      sx={{
        position: 'absolute',
        top: '-40px',
        left: '6px',
        background: 'primary.main',
        color: 'white',
        padding: '8px',
        textDecoration: 'none',
        borderRadius: '4px',
        zIndex: 1000,
        '&:focus': {
          top: '6px',
          transition: 'top 0.3s ease',
        },
        '&:hover': {
          background: 'primary.dark',
        },
      }}
    >
      Skip to main content
    </Box>
  );
}
