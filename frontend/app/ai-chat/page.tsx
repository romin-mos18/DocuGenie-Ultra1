'use client'

import React, { useState, useRef, useEffect } from 'react'

import MainLayout from '../components/layout/MainLayout'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress
} from '@mui/material'
import {
  Send,
  Psychology,
  Person,
  MoreVert,
  Clear,
  VolumeUp,
  ContentCopy,
  ThumbUp,
  ThumbDown
} from '@mui/icons-material'

interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  type?: 'text' | 'document_query' | 'analysis'
  metadata?: {
    confidence?: number
    sources?: string[]
    processing_time?: number
  }
}

export default function AIChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: 'Hello! I\'m DocuGenie AI, your intelligent document assistant. I can help you search documents, extract information, analyze content, and answer questions about your healthcare documents. What would you like to know?',
      sender: 'ai',
      timestamp: new Date(),
      metadata: { confidence: 100 }
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Simulate AI response (replace with actual API call)
      const response = await simulateAIResponse(inputMessage)
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        sender: 'ai',
        timestamp: new Date(),
        type: response.type,
        metadata: response.metadata
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const simulateAIResponse = async (query: string): Promise<{
    content: string
    type: 'text' | 'document_query' | 'analysis'
    metadata: any
  }> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

    const queryLower = query.toLowerCase()

    // Document search queries
    if (queryLower.includes('find') || queryLower.includes('search') || queryLower.includes('show me')) {
      return {
        content: `I found 3 documents related to your query. Here are the most relevant results:

**1. Clinical Trial Protocol - Phase III Oncology**
- Patient ID: PT-456
- Upload Date: January 15, 2024
- OCR Accuracy: 96.8%
- Key entities: Study Protocol, Phase III, Oncology, Safety Data

**2. Lab Report - Blood Analysis**
- Patient ID: PT-789
- Upload Date: January 14, 2024
- OCR Accuracy: 94.2%
- Key entities: Glucose Level, Cholesterol, Complete Blood Count

**3. Informed Consent Form**
- Patient ID: PT-123
- Upload Date: January 13, 2024
- OCR Accuracy: 97.5%
- Key entities: Patient Consent, Clinical Trial, Risk Assessment

Would you like me to analyze any specific document in detail?`,
        type: 'document_query',
        metadata: {
          confidence: 92.5,
          sources: ['Clinical_Trial_Protocol.pdf', 'Lab_Report_001.pdf', 'Consent_Form.docx'],
          processing_time: 1.8
        }
      }
    }

    // Analysis queries
    if (queryLower.includes('analyze') || queryLower.includes('extract') || queryLower.includes('summarize')) {
      return {
        content: `I've analyzed the document and extracted the following key information:

**Document Classification:** Clinical Trial Protocol (Confidence: 96.8%)

**Key Entities Detected:**
- Study ID: ONCO-2024-001
- Protocol Phase: Phase III
- Patient Population: Advanced Lung Cancer
- Primary Endpoint: Overall Survival
- Secondary Endpoints: Progression-Free Survival, Safety
- Study Duration: 24 months
- Target Enrollment: 450 patients

**Compliance Status:**
✅ HIPAA Compliant
✅ ICH-GCP Guidelines Met
✅ FDA 21 CFR Part 11 Ready

**Quality Metrics:**
- OCR Accuracy: 96.8%
- Entity Extraction: 94.2%
- Classification Confidence: 96.8%

Would you like me to dive deeper into any specific aspect?`,
        type: 'analysis',
        metadata: {
          confidence: 96.8,
          processing_time: 2.3
        }
      }
    }

    // General conversation
    const responses = [
      "I can help you with document search, analysis, and information extraction. What specific documents or information are you looking for?",
      "I have access to your document library and can perform advanced searches, entity extraction, and compliance checking. How can I assist you today?",
      "I can analyze documents for key information, check compliance status, and help you find specific content. What would you like me to help you with?",
    ]

    return {
      content: responses[Math.floor(Math.random() * responses.length)],
      type: 'text',
      metadata: {
        confidence: 85 + Math.random() * 15,
        processing_time: 0.5 + Math.random() * 1.0
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleClearChat = () => {
    setMessages([messages[0]]) // Keep the initial AI greeting
    setAnchorEl(null)
  }

  return (
    <MainLayout>
      <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper sx={{ p: 2, mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: '#1976d2', mr: 2 }}>
              <Psychology />
            </Avatar>
            <Box>
              <Typography variant="h6">DocuGenie AI Assistant</Typography>
              <Typography variant="caption" color="text.secondary">
                Conversational Document Intelligence • 20+ Languages • HIPAA Compliant
              </Typography>
            </Box>
          </Box>
          
          <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
            <MoreVert />
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem onClick={handleClearChat}>
              <Clear sx={{ mr: 1 }} />
              Clear Chat
            </MenuItem>
            <MenuItem onClick={() => setAnchorEl(null)}>
              <VolumeUp sx={{ mr: 1 }} />
              Voice Commands
            </MenuItem>
          </Menu>
        </Paper>

        {/* Messages */}
        <Paper sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Box
                  sx={{
                    maxWidth: '70%',
                    display: 'flex',
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                    alignItems: 'flex-start',
                    gap: 1
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.sender === 'user' ? '#1976d2' : '#4caf50',
                      width: 32,
                      height: 32
                    }}
                  >
                    {message.sender === 'user' ? <Person /> : <Psychology />}
                  </Avatar>
                  
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: message.sender === 'user' ? '#1976d2' : '#f5f5f5',
                      color: message.sender === 'user' ? 'white' : 'inherit',
                      borderRadius: 2
                    }}
                  >
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Typography>
                    
                    {message.metadata && (
                      <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {message.metadata.confidence && (
                          <Chip
                            label={`${message.metadata.confidence.toFixed(1)}% confidence`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {message.metadata.processing_time && (
                          <Chip
                            label={`${message.metadata.processing_time.toFixed(1)}s`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    )}
                    
                    <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            ))}
            
            {isLoading && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ bgcolor: '#4caf50', width: 32, height: 32 }}>
                    <Psychology />
                  </Avatar>
                  <Paper sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} />
                      <Typography variant="body2">AI is thinking...</Typography>
                    </Box>
                  </Paper>
                </Box>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>

          {/* Input */}
          <Divider />
          <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask me about documents, search for information, or request analysis..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              <Send />
            </Button>
          </Box>
        </Paper>
              </Box>


      </MainLayout>
    )
  }
