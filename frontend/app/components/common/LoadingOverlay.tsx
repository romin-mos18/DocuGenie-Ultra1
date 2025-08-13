'use client';

import { Box, CircularProgress, Typography, Fade } from '@mui/material';

interface LoadingOverlayProps {
  open: boolean;
  message?: string;
}

export default function LoadingOverlay({ open, message = 'Loading...' }: LoadingOverlayProps) {
  return (
    <Fade in={open}>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          {message}
        </Typography>
      </Box>
    </Fade>
  );
}
