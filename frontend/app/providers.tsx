'use client';

import React, { PropsWithChildren } from 'react';
import { Provider as ReduxProvider } from 'react-redux';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { store } from './store/store';
import { queryClient } from './lib/react-query';
import { WebSocketProvider } from '../lib/websocket/WebSocketProvider';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme/theme';

export default function Providers({ children }: PropsWithChildren) {
  return (
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <WebSocketProvider>
            {children}
            <ReactQueryDevtools initialIsOpen={false} />
          </WebSocketProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ReduxProvider>
  );
}
