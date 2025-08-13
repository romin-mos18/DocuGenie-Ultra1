'use client';

import React from 'react';
import { Box, Container, CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '../../lib/theme';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {children}
        </Box>
      </Container>
    </ThemeProvider>
  );
}
