'use client';

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  Skeleton,
  Card,
  CardContent,
  Divider,
  Grid,
  Chip,
} from '@mui/material';
import {
  WarningAmber,
  HourglassEmpty,
  Error as ErrorIcon,
  Info,
} from '@mui/icons-material';

interface FallbackContentProps {
  type: 'loading' | 'error' | 'empty' | 'processing';
  message?: string;
  details?: string;
}

export const FallbackContent: React.FC<FallbackContentProps> = ({ 
  type, 
  message, 
  details 
}) => {
  const getIcon = () => {
    switch (type) {
      case 'loading':
        return <HourglassEmpty sx={{ fontSize: 48, color: 'primary.main' }} />;
      case 'error':
        return <ErrorIcon sx={{ fontSize: 48, color: 'error.main' }} />;
      case 'empty':
        return <Info sx={{ fontSize: 48, color: 'info.main' }} />;
      case 'processing':
        return <HourglassEmpty sx={{ fontSize: 48, color: 'warning.main' }} />;
      default:
        return <Info sx={{ fontSize: 48, color: 'grey.500' }} />;
    }
  };

  const getMessage = () => {
    if (message) return message;
    
    switch (type) {
      case 'loading':
        return 'Loading document information...';
      case 'error':
        return 'Failed to load document data';
      case 'empty':
        return 'No data available';
      case 'processing':
        return 'Document is being processed';
      default:
        return 'Information unavailable';
    }
  };

  const getDetails = () => {
    if (details) return details;
    
    switch (type) {
      case 'loading':
        return 'Please wait while we fetch the document details.';
      case 'error':
        return 'There was an error loading the document data. Please try refreshing the page.';
      case 'empty':
        return 'This document does not contain the requested information.';
      case 'processing':
        return 'AI analysis is currently in progress. Results will be available shortly.';
      default:
        return 'The requested information is not currently available.';
    }
  };

  const getSeverity = () => {
    switch (type) {
      case 'loading':
      case 'processing':
        return 'info';
      case 'error':
        return 'error';
      case 'empty':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 4 }}>
      {getIcon()}
      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
        {getMessage()}
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', mb: 2 }}>
        {getDetails()}
      </Typography>
      <Alert severity={getSeverity() as any} sx={{ mt: 1 }}>
        <Typography variant="body2">
          {type === 'error' && 'If this problem persists, please contact support.'}
          {type === 'loading' && 'This should only take a few seconds.'}
          {type === 'processing' && 'You can check back in a few moments.'}
          {type === 'empty' && 'Try uploading a different document or check the document format.'}
        </Typography>
      </Alert>
    </Box>
  );
};

export const LoadingSkeleton: React.FC<{ type: 'card' | 'table' | 'list' }> = ({ type }) => {
  if (type === 'card') {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="60%" height={32} />
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            {[...Array(4)].map((_, index) => (
              <React.Fragment key={index}>
                <Grid item xs={6}>
                  <Skeleton variant="text" width="80%" />
                </Grid>
                <Grid item xs={6}>
                  <Skeleton variant="text" width="60%" />
                </Grid>
              </React.Fragment>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  }

  if (type === 'table') {
    return (
      <Box>
        <Skeleton variant="text" width="40%" height={32} sx={{ mb: 2 }} />
        {[...Array(5)].map((_, index) => (
          <Box key={index} sx={{ display: 'flex', gap: 2, mb: 1 }}>
            <Skeleton variant="text" width="25%" />
            <Skeleton variant="text" width="20%" />
            <Skeleton variant="text" width="15%" />
            <Skeleton variant="text" width="25%" />
            <Skeleton variant="text" width="15%" />
          </Box>
        ))}
      </Box>
    );
  }

  if (type === 'list') {
    return (
      <Box>
        <Skeleton variant="text" width="30%" height={32} sx={{ mb: 2 }} />
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {[...Array(8)].map((_, index) => (
            <Skeleton key={index} variant="rectangular" width={80} height={24} sx={{ borderRadius: 3 }} />
          ))}
        </Box>
      </Box>
    );
  }

  return null;
};

export const EmptyState: React.FC<{
  title: string;
  description: string;
  icon?: React.ReactNode;
}> = ({ title, description, icon }) => {
  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      p: 4,
      textAlign: 'center'
    }}>
      {icon || <Info sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />}
      <Typography variant="h6" color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        {description}
      </Typography>
    </Box>
  );
};

export default FallbackContent;
