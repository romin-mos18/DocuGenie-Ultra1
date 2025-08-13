'use client';

import { useState } from 'react';
import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Avatar, Badge } from '@mui/material';
import { Menu as MenuIcon, Notifications, Person, Accessibility } from '@mui/icons-material';
import Link from 'next/link';
import { handleKeyboardNavigation } from '../../../lib/accessibility';
import AccessibilityPreferences from '../common/AccessibilityPreferences';

interface HeaderProps {
  onMenuToggle: () => void;
}

export default function Header({ onMenuToggle }: HeaderProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);
  const [accessibilityOpen, setAccessibilityOpen] = useState(false);
  const isMenuOpen = Boolean(anchorEl);
  const isNotificationsOpen = Boolean(notificationAnchor);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsClose = () => {
    setNotificationAnchor(null);
  };

  const handleAccessibilityOpen = () => {
    setAccessibilityOpen(true);
  };

  const handleAccessibilityClose = () => {
    setAccessibilityOpen(false);
  };

  const handleLogout = () => {
    // TODO: Implement logout logic
    handleMenuClose();
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    handleKeyboardNavigation(event, undefined, handleMenuClose);
  };

  const handleNotificationKeyDown = (event: React.KeyboardEvent) => {
    handleKeyboardNavigation(event, undefined, handleNotificationsClose);
  };

  return (
    <AppBar 
      position="fixed" 
      sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      role="banner"
      aria-label="Main navigation"
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="Toggle navigation menu"
          aria-expanded={false}
          aria-controls="navigation-menu"
          edge="start"
          onClick={onMenuToggle}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography 
          variant="h6" 
          noWrap 
          component="div" 
          sx={{ flexGrow: 1 }}
          role="heading"
          aria-level={1}
        >
          <Link 
            href="/" 
            style={{ color: 'inherit', textDecoration: 'none' }}
            aria-label="Go to homepage"
          >
            DocuGenie Ultra
          </Link>
        </Typography>

        <IconButton 
          color="inherit" 
          onClick={handleNotificationsOpen}
          aria-label="View notifications"
          aria-expanded={isNotificationsOpen}
          aria-haspopup="true"
          aria-controls="notifications-menu"
          onKeyDown={handleNotificationKeyDown}
        >
          <Badge badgeContent={2} color="error">
            <Notifications />
          </Badge>
        </IconButton>

        <IconButton
          color="inherit"
          onClick={handleAccessibilityOpen}
          aria-label="Accessibility preferences"
          aria-describedby="accessibility-help"
        >
          <Accessibility />
        </IconButton>

        <IconButton
          onClick={handleProfileMenuOpen}
          size="large"
          edge="end"
          aria-label="User account menu"
          aria-expanded={isMenuOpen}
          aria-haspopup="true"
          aria-controls="profile-menu"
          color="inherit"
          onKeyDown={handleKeyDown}
        >
          <Avatar sx={{ width: 32, height: 32 }} aria-hidden="true">
            <Person />
          </Avatar>
        </IconButton>

        {/* Profile Menu */}
        <Menu
          id="profile-menu"
          anchorEl={anchorEl}
          open={isMenuOpen}
          onClose={handleMenuClose}
          onClick={handleMenuClose}
          role="menu"
          aria-label="User account options"
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem component={Link} href="/profile" role="menuitem">
            Profile
          </MenuItem>
          <MenuItem component={Link} href="/settings" role="menuitem">
            Settings
          </MenuItem>
          <MenuItem onClick={handleLogout} role="menuitem">Logout</MenuItem>
        </Menu>

        {/* Notifications Menu */}
        <Menu
          id="notifications-menu"
          anchorEl={notificationAnchor}
          open={isNotificationsOpen}
          onClose={handleNotificationsClose}
          onClick={handleNotificationsClose}
          role="menu"
          aria-label="Notifications"
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem role="menuitem">
            <Typography variant="inherit" noWrap>
              Document processing complete
            </Typography>
          </MenuItem>
          <MenuItem role="menuitem">
            <Typography variant="inherit" noWrap>
              New document uploaded
            </Typography>
          </MenuItem>
        </Menu>
      </Toolbar>

      {/* Accessibility Preferences Dialog */}
      <AccessibilityPreferences
        open={accessibilityOpen}
        onClose={handleAccessibilityClose}
      />
    </AppBar>
  );
}
