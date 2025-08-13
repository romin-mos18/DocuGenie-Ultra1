'use client'

import React, { useState } from 'react'
import MainLayout from '../components/layout/MainLayout'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Divider,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material'
import {
  Security,
  Psychology,
  Storage,
  Notifications,
  CloudUpload,
  Api,
  Speed,
  Visibility,
  Save,
  RestartAlt
} from '@mui/icons-material'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // AI Settings
    ocrEngine: 'paddleocr',
    ocrConfidenceThreshold: 85,
    classificationThreshold: 90,
    enableFallbackOCR: true,
    enableEntityExtraction: true,
    
    // Security Settings
    enableAuditLog: true,
    enableEncryption: true,
    sessionTimeout: 60,
    maxLoginAttempts: 5,
    enableTwoFA: false,
    
    // Processing Settings
    maxFileSize: 100,
    supportedFormats: ['pdf', 'png', 'jpg', 'jpeg', 'docx'],
    processingTimeout: 300,
    enableAsyncProcessing: true,
    
    // Notification Settings
    emailNotifications: true,
    systemNotifications: true,
    processCompleteNotifications: true,
    errorNotifications: true,
    
    // System Settings
    autoBackup: true,
    backupFrequency: 'daily',
    logLevel: 'info',
    enableMetrics: true
  })

  const handleSwitchChange = (setting: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings(prev => ({
      ...prev,
      [setting]: event.target.checked
    }))
  }

  const handleSliderChange = (setting: string) => (event: Event, newValue: number | number[]) => {
    setSettings(prev => ({
      ...prev,
      [setting]: newValue as number
    }))
  }

  const handleSelectChange = (setting: string) => (event: any) => {
    setSettings(prev => ({
      ...prev,
      [setting]: event.target.value
    }))
  }

  const handleSave = () => {
    // Save settings logic
    alert('Settings saved successfully!')
  }

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight="bold">
              System Settings
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Configure DocuGenie Ultra settings and preferences
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="outlined" startIcon={<RestartAlt />}>
              Reset to Defaults
            </Button>
            <Button variant="contained" startIcon={<Save />} onClick={handleSave}>
              Save Changes
            </Button>
          </Box>
        </Box>

        <Grid container spacing={4}>
          {/* AI Processing Settings */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Psychology sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">AI Processing Settings</Typography>
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Primary OCR Engine</InputLabel>
                      <Select
                        value={settings.ocrEngine}
                        label="Primary OCR Engine"
                        onChange={handleSelectChange('ocrEngine')}
                      >
                        <MenuItem value="paddleocr">PaddleOCR (Recommended)</MenuItem>
                        <MenuItem value="trocr">TrOCR (Handwriting)</MenuItem>
                        <MenuItem value="tesseract">Tesseract</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      OCR Confidence Threshold: {settings.ocrConfidenceThreshold}%
                    </Typography>
                    <Slider
                      value={settings.ocrConfidenceThreshold}
                      onChange={handleSliderChange('ocrConfidenceThreshold')}
                      aria-labelledby="ocr-confidence-slider"
                      valueLabelDisplay="auto"
                      step={5}
                      marks
                      min={50}
                      max={100}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Classification Threshold: {settings.classificationThreshold}%
                    </Typography>
                    <Slider
                      value={settings.classificationThreshold}
                      onChange={handleSliderChange('classificationThreshold')}
                      aria-labelledby="classification-threshold-slider"
                      valueLabelDisplay="auto"
                      step={5}
                      marks
                      min={50}
                      max={100}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableFallbackOCR}
                          onChange={handleSwitchChange('enableFallbackOCR')}
                        />
                      }
                      label="Enable Fallback OCR Engine"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableEntityExtraction}
                          onChange={handleSwitchChange('enableEntityExtraction')}
                        />
                      }
                      label="Enable Medical Entity Extraction"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Security Settings */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Security sx={{ mr: 2, color: 'error.main' }} />
                  <Typography variant="h6">Security Settings</Typography>
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableAuditLog}
                          onChange={handleSwitchChange('enableAuditLog')}
                        />
                      }
                      label="Enable HIPAA Audit Logging"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableEncryption}
                          onChange={handleSwitchChange('enableEncryption')}
                        />
                      }
                      label="Enable Data Encryption at Rest"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Session Timeout (minutes)"
                      type="number"
                      value={settings.sessionTimeout}
                      onChange={(e) => setSettings(prev => ({...prev, sessionTimeout: parseInt(e.target.value)}))}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Max Login Attempts"
                      type="number"
                      value={settings.maxLoginAttempts}
                      onChange={(e) => setSettings(prev => ({...prev, maxLoginAttempts: parseInt(e.target.value)}))}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableTwoFA}
                          onChange={handleSwitchChange('enableTwoFA')}
                        />
                      }
                      label="Enable Two-Factor Authentication"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* File Processing Settings */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <CloudUpload sx={{ mr: 2, color: 'info.main' }} />
                  <Typography variant="h6">File Processing Settings</Typography>
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Maximum File Size (MB)"
                      type="number"
                      value={settings.maxFileSize}
                      onChange={(e) => setSettings(prev => ({...prev, maxFileSize: parseInt(e.target.value)}))}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Supported File Formats
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {settings.supportedFormats.map((format) => (
                        <Chip key={format} label={format.toUpperCase()} size="small" />
                      ))}
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Processing Timeout (seconds)"
                      type="number"
                      value={settings.processingTimeout}
                      onChange={(e) => setSettings(prev => ({...prev, processingTimeout: parseInt(e.target.value)}))}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableAsyncProcessing}
                          onChange={handleSwitchChange('enableAsyncProcessing')}
                        />
                      }
                      label="Enable Asynchronous Processing"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Notification Settings */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Notifications sx={{ mr: 2, color: 'warning.main' }} />
                  <Typography variant="h6">Notification Settings</Typography>
                </Box>
                
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Notifications />
                    </ListItemIcon>
                    <ListItemText primary="Email Notifications" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.emailNotifications}
                        onChange={handleSwitchChange('emailNotifications')}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      <Api />
                    </ListItemIcon>
                    <ListItemText primary="System Notifications" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.systemNotifications}
                        onChange={handleSwitchChange('systemNotifications')}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      <Speed />
                    </ListItemIcon>
                    <ListItemText primary="Processing Complete" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.processCompleteNotifications}
                        onChange={handleSwitchChange('processCompleteNotifications')}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      <Visibility />
                    </ListItemIcon>
                    <ListItemText primary="Error Notifications" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.errorNotifications}
                        onChange={handleSwitchChange('errorNotifications')}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* System Settings */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Storage sx={{ mr: 2, color: 'success.main' }} />
                  <Typography variant="h6">System Settings</Typography>
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.autoBackup}
                          onChange={handleSwitchChange('autoBackup')}
                        />
                      }
                      label="Enable Automatic Backups"
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Backup Frequency</InputLabel>
                      <Select
                        value={settings.backupFrequency}
                        label="Backup Frequency"
                        onChange={handleSelectChange('backupFrequency')}
                        disabled={!settings.autoBackup}
                      >
                        <MenuItem value="hourly">Hourly</MenuItem>
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="weekly">Weekly</MenuItem>
                        <MenuItem value="monthly">Monthly</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>System Log Level</InputLabel>
                      <Select
                        value={settings.logLevel}
                        label="System Log Level"
                        onChange={handleSelectChange('logLevel')}
                      >
                        <MenuItem value="debug">Debug</MenuItem>
                        <MenuItem value="info">Info</MenuItem>
                        <MenuItem value="warning">Warning</MenuItem>
                        <MenuItem value="error">Error</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableMetrics}
                          onChange={handleSwitchChange('enableMetrics')}
                        />
                      }
                      label="Enable Performance Metrics"
                    />
                  </Grid>
                </Grid>

                <Divider sx={{ my: 3 }} />
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  Some settings require a system restart to take effect. You will be notified if a restart is needed.
                </Alert>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                  <Button variant="outlined" startIcon={<RestartAlt />}>
                    Reset to Defaults
                  </Button>
                  <Button variant="contained" startIcon={<Save />} onClick={handleSave}>
                    Save All Settings
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
              </Box>


      </MainLayout>
    )
  }
