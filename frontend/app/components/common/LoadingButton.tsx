'use client';

import { Button, ButtonProps, CircularProgress } from '@mui/material';

interface LoadingButtonProps extends ButtonProps {
  loading?: boolean;
  loadingText?: string;
}

export default function LoadingButton({
  loading = false,
  loadingText = 'Loading...',
  disabled,
  children,
  ...props
}: LoadingButtonProps) {
  return (
    <Button
      disabled={loading || disabled}
      {...props}
    >
      {loading ? (
        <>
          <CircularProgress
            size={24}
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              marginTop: '-12px',
              marginLeft: '-12px',
            }}
          />
          <span style={{ visibility: 'hidden' }}>{children}</span>
        </>
      ) : (
        children
      )}
    </Button>
  );
}
