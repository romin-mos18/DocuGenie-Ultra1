'use client'

import React, { useState } from 'react'

import MainLayout from '../components/layout/MainLayout'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material'
import {
  Search,
  FilterList,
  GraphicEq,
  Timeline,
  Psychology,
  ExpandMore,
  Visibility,
  GetApp
} from '@mui/icons-material'

interface SearchResult {
  id: string
  filename: string
  document_type: string
  semantic_score?: number
  _score?: number
  entities: string[]
  upload_time: string
  size: string
  ocr_accuracy: string
}

export default function AdvancedSearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchType, setSearchType] = useState(0) // 0: Semantic, 1: Elasticsearch, 2: Graph
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [graphData, setGraphData] = useState<any>(null)
  const [searchStats, setSearchStats] = useState<any>(null)

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setSearchResults([])
    setGraphData(null)

    try {
      let response
      let data

      if (searchType === 0) {
        // Semantic Vector Search
        response = await fetch('http://localhost:8007/api/search/semantic', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: searchQuery,
            search_type: 'semantic',
            limit: 10
          })
        })
        data = await response.json()
        setSearchResults(data.results || [])
        setSearchStats({
          type: 'Semantic Vector Search',
          total_found: data.total_found,
          processing_time: data.processing_time
        })
      } else if (searchType === 1) {
        // Elasticsearch
        response = await fetch(`http://localhost:8007/api/search/elasticsearch?q=${encodeURIComponent(searchQuery)}&size=10`)
        data = await response.json()
        setSearchResults(data.hits?.hits || [])
        setSearchStats({
          type: 'Elasticsearch Full-Text',
          total_found: data.hits?.total?.value || 0,
          processing_time: `${data.took}ms`
        })
      } else if (searchType === 2) {
        // Knowledge Graph
        response = await fetch('http://localhost:8007/api/search/graph', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            entity: searchQuery,
            depth: 2
          })
        })
        data = await response.json()
        setGraphData(data)
        setSearchStats({
          type: 'Knowledge Graph Traversal',
          total_nodes: data.total_nodes,
          total_edges: data.total_edges
        })
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const renderSearchResults = () => {
    if (searchType === 2 && graphData) {
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            Knowledge Graph Results
          </Typography>
          <Grid container spacing={2}>
            {graphData.graph.nodes.map((node: any, index: number) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" color={node.type === 'document' ? 'primary' : 'secondary'}>
                      {node.type === 'document' ? '📄 Document' : '🏷️ Entity'}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {node.label}
                    </Typography>
                    {node.properties && (
                      <Box sx={{ mt: 1 }}>
                        {Object.entries(node.properties).map(([key, value]: [string, any]) => (
                          <Chip
                            key={key}
                            label={`${key}: ${value}`}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )
    }

    return (
      <List>
        {searchResults.map((result, index) => (
          <ListItem key={result.id || index} divider>
            <Card sx={{ width: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    {result.filename}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<Visibility />}>View</Button>
                    <Button size="small" startIcon={<GetApp />}>Download</Button>
                  </Box>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Chip label={result.document_type} color="primary" size="small" sx={{ mr: 1 }} />
                  <Chip label={result.size} size="small" sx={{ mr: 1 }} />
                  <Chip label={`OCR: ${result.ocr_accuracy}`} size="small" sx={{ mr: 1 }} />
                  {result.semantic_score && (
                    <Chip 
                      label={`Similarity: ${(result.semantic_score * 100).toFixed(1)}%`} 
                      color="secondary" 
                      size="small" 
                    />
                  )}
                  {result._score && (
                    <Chip 
                      label={`Score: ${result._score.toFixed(1)}`} 
                      color="secondary" 
                      size="small" 
                    />
                  )}
                </Box>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="body2">
                      Extracted Entities ({result.entities?.length || 0})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {result.entities?.map((entity, idx) => (
                        <Chip key={idx} label={entity} variant="outlined" size="small" />
                      ))}
                    </Box>
                  </AccordionDetails>
                </Accordion>

                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Uploaded: {result.upload_time}
                </Typography>
              </CardContent>
            </Card>
          </ListItem>
        ))}
      </List>
    )
  }

  return (
    <MainLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Advanced Document Search
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Powered by Vector Search, Knowledge Graphs, and Elasticsearch
        </Typography>

        {/* Search Interface */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ mb: 2 }}>
            <Tabs value={searchType} onChange={(e, newValue) => setSearchType(newValue)}>
              <Tab icon={<Psychology />} label="Semantic Vector" />
              <Tab icon={<Search />} label="Full-Text (Elasticsearch)" />
              <Tab icon={<Timeline />} label="Knowledge Graph" />
            </Tabs>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={
                searchType === 0 ? "Describe what you're looking for (e.g., 'oncology clinical trial protocols')" :
                searchType === 1 ? "Enter keywords to search document content" :
                "Enter entity name to explore relationships (e.g., 'Patient ID', 'Drug Name')"
              }
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isSearching}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={!searchQuery.trim() || isSearching}
              startIcon={isSearching ? <CircularProgress size={20} /> : <Search />}
              sx={{ minWidth: 120 }}
            >
              {isSearching ? 'Searching...' : 'Search'}
            </Button>
          </Box>

          {/* Search Type Info */}
          <Alert severity="info" sx={{ mb: 2 }}>
            {searchType === 0 && (
              <Typography variant="body2">
                <strong>Semantic Vector Search:</strong> Uses AI embeddings to find documents by meaning, not just keywords. 
                Great for conceptual searches and finding related content.
              </Typography>
            )}
            {searchType === 1 && (
              <Typography variant="body2">
                <strong>Elasticsearch Full-Text:</strong> Traditional keyword search with highlighting and relevance scoring. 
                Perfect for finding specific terms and phrases.
              </Typography>
            )}
            {searchType === 2 && (
              <Typography variant="body2">
                <strong>Knowledge Graph:</strong> Explores relationships between entities in your documents. 
                Discovers connections between patients, providers, studies, and more.
              </Typography>
            )}
          </Alert>
        </Paper>

        {/* Search Results */}
        {searchStats && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Search Results - {searchStats.type}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip label={`Found: ${searchStats.total_found || searchStats.total_nodes || 0}`} />
              <Chip label={`Time: ${searchStats.processing_time || 'N/A'}`} />
              {searchStats.total_edges && (
                <Chip label={`Relationships: ${searchStats.total_edges}`} />
              )}
            </Box>
          </Paper>
        )}

        {(searchResults.length > 0 || graphData) && (
          <Paper sx={{ p: 2 }}>
            {renderSearchResults()}
          </Paper>
        )}

        {!isSearching && searchQuery && searchResults.length === 0 && !graphData && searchStats && (
          <Alert severity="warning">
            No results found for "{searchQuery}". Try different keywords or search type.
          </Alert>
        )}
              </Box>


      </MainLayout>
    )
  }
