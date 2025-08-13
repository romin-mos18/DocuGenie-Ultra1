'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormControlLabel,
  Switch,
  Typography,
  Box,
  Slider,
  Divider,
  Alert,
} from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibilityPreferencesProps {
  open: boolean;
  onClose: () => void;
}

interface Preferences {
  highContrast: boolean;
  reducedMotion: boolean;
  largeText: boolean;
  focusIndicators: boolean;
  screenReaderAnnouncements: boolean;
  keyboardNavigation: boolean;
  fontSize: number;
  animationSpeed: number;
}

export default function AccessibilityPreferences({
  open,
  onClose,
}: AccessibilityPreferencesProps) {
  const { announceSuccess, announceError } = useAccessibility();
  const [preferences, setPreferences] = useState<Preferences>({
    highContrast: false,
    reducedMotion: false,
    largeText: false,
    focusIndicators: true,
    screenReaderAnnouncements: true,
    keyboardNavigation: true,
    fontSize: 16,
    animationSpeed: 1,
  });

  const handlePreferenceChange = (key: keyof Preferences, value: boolean | number) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = () => {
    try {
      // Save preferences to localStorage (only in browser)
      if (typeof window !== 'undefined') {
        localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
      }
      
      // Apply preferences to the document
      applyPreferences(preferences);
      
      announceSuccess('Accessibility preferences saved successfully');
      onClose();
    } catch (error) {
      announceError('Failed to save accessibility preferences');
    }
  };

  const applyPreferences = (prefs: Preferences) => {
    const root = document.documentElement;
    
    // Apply high contrast
    if (prefs.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    // Apply reduced motion
    if (prefs.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }
    
    // Apply large text
    if (prefs.largeText) {
      root.style.fontSize = '18px';
    } else {
      root.style.fontSize = '16px';
    }
    
    // Apply custom font size
    root.style.setProperty('--font-size', `${prefs.fontSize}px`);
    
    // Apply animation speed
    root.style.setProperty('--animation-speed', `${prefs.animationSpeed}s`);
  };

  const handleReset = () => {
    const defaultPreferences: Preferences = {
      highContrast: false,
      reducedMotion: false,
      largeText: false,
      focusIndicators: true,
      screenReaderAnnouncements: true,
      keyboardNavigation: true,
      fontSize: 16,
      animationSpeed: 1,
    };
    
    setPreferences(defaultPreferences);
    announceSuccess('Preferences reset to default');
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="accessibility-preferences-title"
      aria-describedby="accessibility-preferences-description"
    >
      <DialogTitle id="accessibility-preferences-title">
        Accessibility Preferences
      </DialogTitle>
      
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Customize your experience to make the application more accessible for your needs.
        </Typography>

        <Alert severity="info" sx={{ mb: 3 }}>
          These settings will be saved to your browser and applied immediately.
        </Alert>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Visual Preferences */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Visual Preferences
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.highContrast}
                  onChange={(e) => handlePreferenceChange('highContrast', e.target.checked)}
                />
              }
              label="High Contrast Mode"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.largeText}
                  onChange={(e) => handlePreferenceChange('largeText', e.target.checked)}
                />
              }
              label="Large Text"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.focusIndicators}
                  onChange={(e) => handlePreferenceChange('focusIndicators', e.target.checked)}
                />
              }
              label="Enhanced Focus Indicators"
            />
          </Box>

          <Divider />

          {/* Motion Preferences */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Motion Preferences
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.reducedMotion}
                  onChange={(e) => handlePreferenceChange('reducedMotion', e.target.checked)}
                />
              }
              label="Reduced Motion"
            />
            
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom>Animation Speed</Typography>
              <Slider
                value={preferences.animationSpeed}
                onChange={(_, value) => handlePreferenceChange('animationSpeed', value as number)}
                min={0.1}
                max={2}
                step={0.1}
                marks={[
                  { value: 0.1, label: 'Slow' },
                  { value: 1, label: 'Normal' },
                  { value: 2, label: 'Fast' },
                ]}
                valueLabelDisplay="auto"
              />
            </Box>
          </Box>

          <Divider />

          {/* Font Size */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Text Size
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom>Font Size: {preferences.fontSize}px</Typography>
              <Slider
                value={preferences.fontSize}
                onChange={(_, value) => handlePreferenceChange('fontSize', value as number)}
                min={12}
                max={24}
                step={1}
                marks={[
                  { value: 12, label: 'Small' },
                  { value: 16, label: 'Normal' },
                  { value: 24, label: 'Large' },
                ]}
                valueLabelDisplay="auto"
              />
            </Box>
          </Box>

          <Divider />

          {/* Screen Reader Preferences */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Screen Reader Preferences
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.screenReaderAnnouncements}
                  onChange={(e) => handlePreferenceChange('screenReaderAnnouncements', e.target.checked)}
                />
              }
              label="Screen Reader Announcements"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.keyboardNavigation}
                  onChange={(e) => handlePreferenceChange('keyboardNavigation', e.target.checked)}
                />
              }
              label="Enhanced Keyboard Navigation"
            />
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleReset} color="secondary">
          Reset to Default
        </Button>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained">
          Save Preferences
        </Button>
      </DialogActions>
    </Dialog>
  );
}
