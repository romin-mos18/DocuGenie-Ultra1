'use client';

import { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Divider,
  Box,
} from '@mui/material';
import {
  Description,
  Upload,
  Analytics,
  Settings,
  ExpandLess,
  ExpandMore,
  Dashboard,
  Assessment,
  Group,
  Science,
} from '@mui/icons-material';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { handleKeyboardNavigation } from '../../../lib/accessibility';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  drawerWidth?: number;
}

export default function Sidebar({ open, onClose, drawerWidth = 240 }: SidebarProps) {
  const pathname = usePathname();
  const [documentsOpen, setDocumentsOpen] = useState(true);
  const [aiOpen, setAiOpen] = useState(false);

  const handleDocumentsClick = () => {
    setDocumentsOpen(!documentsOpen);
  };

  const handleAiClick = () => {
    setAiOpen(!aiOpen);
  };

  const isActive = (path: string) => pathname === path;

  return (
    <Drawer
      variant="permanent"
      open={open}
      onClose={onClose}
      role="navigation"
      aria-label="Main navigation"
      id="navigation-menu"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          ...(open && {
            transition: (theme) =>
              theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
          }),
          ...(!open && {
            transition: (theme) =>
              theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
              }),
            width: (theme) => theme.spacing(7),
          }),
        },
      }}
    >
      <Box sx={{ overflow: 'auto', mt: 8 }}>
        <List>
          <ListItem disablePadding>
            <ListItemButton 
              component={Link} 
              href="/dashboard" 
              selected={isActive('/dashboard')}
              aria-label="Go to dashboard"
            >
              <ListItemIcon>
                <Dashboard />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton 
              onClick={handleDocumentsClick}
              aria-expanded={documentsOpen}
              aria-controls="documents-submenu"
              aria-label="Documents menu"
            >
              <ListItemIcon>
                <Description />
              </ListItemIcon>
              <ListItemText primary="Documents" />
              {documentsOpen ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>

          <Collapse in={documentsOpen} timeout="auto" unmountOnExit id="documents-submenu">
            <List component="div" disablePadding role="group" aria-label="Document options">
              <ListItemButton
                sx={{ pl: 4 }}
                component={Link}
                href="/documents/upload"
                selected={isActive('/documents/upload')}
                aria-label="Upload documents"
              >
                <ListItemIcon>
                  <Upload />
                </ListItemIcon>
                <ListItemText primary="Upload" />
              </ListItemButton>

              <ListItemButton
                sx={{ pl: 4 }}
                component={Link}
                href="/documents"
                selected={isActive('/documents')}
                aria-label="View all documents"
              >
                <ListItemIcon>
                  <Description />
                </ListItemIcon>
                <ListItemText primary="All Documents" />
              </ListItemButton>
            </List>
          </Collapse>

          <ListItem disablePadding>
            <ListItemButton 
              onClick={handleAiClick}
              aria-expanded={aiOpen}
              aria-controls="ai-submenu"
              aria-label="AI Features menu"
            >
              <ListItemIcon>
                <Science />
              </ListItemIcon>
              <ListItemText primary="AI Features" />
              {aiOpen ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>

          <Collapse in={aiOpen} timeout="auto" unmountOnExit id="ai-submenu">
            <List component="div" disablePadding role="group" aria-label="AI Features options">
              <ListItemButton
                sx={{ pl: 4 }}
                component={Link}
                href="/ai/processing"
                selected={isActive('/ai/processing')}
                aria-label="AI document processing"
              >
                <ListItemIcon>
                  <Analytics />
                </ListItemIcon>
                <ListItemText primary="Processing" />
              </ListItemButton>

              <ListItemButton
                sx={{ pl: 4 }}
                component={Link}
                href="/ai/analytics"
                selected={isActive('/ai/analytics')}
                aria-label="AI analytics"
              >
                <ListItemIcon>
                  <Assessment />
                </ListItemIcon>
                <ListItemText primary="Analytics" />
              </ListItemButton>
            </List>
          </Collapse>
        </List>

        <Divider />

        <List>
          <ListItem disablePadding>
            <ListItemButton 
              component={Link} 
              href="/users" 
              selected={isActive('/users')}
              aria-label="Manage users"
            >
              <ListItemIcon>
                <Group />
              </ListItemIcon>
              <ListItemText primary="Users" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton 
              component={Link} 
              href="/settings" 
              selected={isActive('/settings')}
              aria-label="Application settings"
            >
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
}
