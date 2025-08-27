import React from 'react'
import { Container, Typography, Box } from '@mui/material'
import { StockSearch } from './components/StockSearch'

function App() {
  return (
    <Container>
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Stock Analyzer
        </Typography>
        <StockSearch />
      </Box>
    </Container>
  )
}

export default App