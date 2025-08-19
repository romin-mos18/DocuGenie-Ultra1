'use client';

import React from 'react';
import { Box, Paper, Typography, Button, Alert } from '@mui/material';
import { Error as ErrorIcon, Refresh } from '@mui/icons-material';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; retry: () => void }>;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} retry={this.handleRetry} />;
      }

      return (
        <Box sx={{ p: 3 }}>
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
            
            <Typography variant="h5" gutterBottom>
              Something went wrong
            </Typography>
            
            <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
              An unexpected error occurred while rendering this component.
              Please try refreshing or contact support if the problem persists.
            </Typography>

            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={this.handleRetry}
              sx={{ mb: 3 }}
            >
              Try Again
            </Button>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Alert severity="error" sx={{ textAlign: 'left', mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Error Details (Development Mode):
                </Typography>
                <Typography variant="body2" component="pre" sx={{ fontSize: '0.8rem' }}>
                  {this.state.error.message}
                  {this.state.error.stack && (
                    <>
                      {'\n\nStack Trace:\n'}
                      {this.state.error.stack}
                    </>
                  )}
                </Typography>
              </Alert>
            )}
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = () => setError(null);

  const handleError = React.useCallback((error: Error) => {
    console.error('Error caught by useErrorHandler:', error);
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { handleError, resetError };
};

// Wrapper component for functional error handling
export const SafeComponent: React.FC<{
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; retry: () => void }>;
}> = ({ children, fallback }) => {
  return (
    <ErrorBoundary fallback={fallback}>
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundary;