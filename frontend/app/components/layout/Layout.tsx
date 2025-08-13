'use client';

import { useState } from 'react';
import { Box, CssBaseline, Container } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import SkipLink from '../common/SkipLink';

interface LayoutProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 240;

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      <SkipLink />
      
      {/* Header */}
      <Header onMenuToggle={handleSidebarToggle} />

      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onClose={handleSidebarToggle} drawerWidth={DRAWER_WIDTH} />

      {/* Main Content */}
      <Box
        component="main"
        id="main-content"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8, // Space for fixed header
          mb: 8, // Space for footer
        }}
      >
        <Container maxWidth="lg">
          {children}
        </Container>
      </Box>

      {/* Footer */}
      <Footer />
    </Box>
  );
}
