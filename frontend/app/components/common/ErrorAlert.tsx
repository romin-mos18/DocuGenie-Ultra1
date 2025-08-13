'use client';

import { Alert, AlertTitle, Box, Button } from '@mui/material';
import { Refresh } from '@mui/icons-material';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export default function ErrorAlert({
  title = 'Error',
  message,
  onRetry,
}: ErrorAlertProps) {
  return (
    <Box sx={{ my: 2 }}>
      <Alert
        severity="error"
        action={
          onRetry && (
            <Button
              color="inherit"
              size="small"
              startIcon={<Refresh />}
              onClick={onRetry}
            >
              Retry
            </Button>
          )
        }
      >
        <AlertTitle>{title}</AlertTitle>
        {message}
      </Alert>
    </Box>
  );
}
