'use client';

import { Suspense } from 'react';
import ErrorBoundary from './ErrorBoundary';
import LoadingSpinner from './LoadingSpinner';

interface AsyncBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  loadingMessage?: string;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export default function AsyncBoundary({
  children,
  fallback,
  errorFallback,
  loadingMessage,
  onError,
}: AsyncBoundaryProps) {
  return (
    <ErrorBoundary fallback={errorFallback} onError={onError}>
      <Suspense fallback={fallback || <LoadingSpinner message={loadingMessage} />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}
