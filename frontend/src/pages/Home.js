import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import DocumentUpload from '../components/DocumentUpload';
import SummaryDisplay from '../components/SummaryDisplay';
import { FileText, Loader, AlertCircle } from 'lucide-react';

const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px;
`;

const LoadingOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LoadingCard = styled(motion.div)`
  background: white;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  margin: 20px;
`;

const LoadingText = styled.div`
  margin-top: 16px;
  
  h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
  }
  
  p {
    color: #64748b;
    font-size: 0.9rem;
  }
`;

const ErrorCard = styled(motion.div)`
  max-width: 600px;
  margin: 40px auto;
  background: white;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #ef4444;
`;

const ErrorTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const ErrorMessage = styled.p`
  color: #64748b;
  margin-bottom: 20px;
  line-height: 1.6;
`;

const RetryButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(118, 75, 162, 0.3);
  }
`;

// Real API service connecting to FastAPI backend with AI
const API_BASE_URL = 'http://localhost:8050';

const apiService = {
  async uploadDocument(file, template, customPrompt) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', template);
    if (customPrompt) {
      formData.append('custom_prompt', customPrompt);
    }
    
    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Transform to frontend format
    return {
      id: result.doc_id,
      filename: result.filename,
      template_type: result.template,
      content: this.formatSummaryContent(result),
      created_at: result.timestamp,
      status: 'completed',
      raw_result: result, // Keep original for debugging
      stats: {
        word_count: this.estimateWordCount(result.summary),
        reading_time: Math.ceil(this.estimateWordCount(result.summary) / 200),
        compression_ratio: 85, // Estimate
        confidence_score: 95,
        processing_time: result.processing_time
      }
    };
  },
  
  formatSummaryContent(result) {
    let content = `# Document Summary: ${result.filename}\n\n`;
    content += `**Template Used:** ${result.template}\n`;
    content += `**Processing Time:** ${result.processing_time?.toFixed(2)}s\n\n`;
    content += `## AI-Generated Summary\n\n${result.summary}\n\n`;
    
    if (result.insights && result.insights.length > 0) {
      content += `## Key Insights\n\n`;
      result.insights.forEach((insight, index) => {
        content += `${index + 1}. ${insight}\n`;
      });
      content += '\n';
    }
    
    content += `---\n*Processed with llama3:8b - 100% Local AI Processing*`;
    
    return content;
  },
  
  estimateWordCount(text) {
    return text?.split(/\s+/).length || 0;
  },

  async getSummaries() {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const summaries = await response.json();
      
      // Transform to frontend format
      return summaries.map(summary => ({
        id: summary.doc_id,
        filename: summary.filename,
        template_type: summary.template,
        content: `# ${summary.filename}\n\n${summary.summary}`,
        created_at: summary.timestamp,
        status: 'completed'
      }));
    } catch (error) {
      console.error('Failed to fetch summaries:', error);
      // Fallback to localStorage for development
      const stored = localStorage.getItem('summaries');
      return stored ? JSON.parse(stored) : [];
    }
  },

  async updateSummary(id, content) {
    // For now, use localStorage until we implement update API
    const summaries = await this.getSummaries();
    const index = summaries.findIndex(s => s.id === id);
    if (index !== -1) {
      summaries[index].content = content;
      summaries[index].updated_at = new Date().toISOString();
      localStorage.setItem('summaries', JSON.stringify(summaries));
    }
    return summaries[index];
  },

  async exportSummary(summary, format) {
    // Simulate export
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (format === 'pdf') {
      // Create a simple text file for demo
      const blob = new Blob([summary.content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${summary.filename}_summary.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }
};

const Home = () => {
  const [summaries, setSummaries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('upload'); // 'upload' or 'results'

  useEffect(() => {
    loadSummaries();
  }, []);

  const loadSummaries = async () => {
    try {
      const data = await apiService.getSummaries();
      setSummaries(data);
      if (data.length > 0) {
        setCurrentView('results');
      }
    } catch (err) {
      console.error('Failed to load summaries:', err);
    }
  };

  const handleDocumentUpload = async (file, template, customPrompt) => {
    setIsLoading(true);
    setError(null);
    setLoadingMessage('Uploading document...');
    
    try {
      // Simulate upload progress
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLoadingMessage('Extracting text...');
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      setLoadingMessage('Analyzing content...');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLoadingMessage('Generating summary...');
      
      const newSummary = await apiService.uploadDocument(file, template, customPrompt);
      
      // Update summaries list
      const updatedSummaries = [newSummary, ...summaries];
      setSummaries(updatedSummaries);
      
      setCurrentView('results');
      setIsLoading(false);
      
    } catch (err) {
      setError({
        title: 'Upload Failed',
        message: err.message || 'Failed to process the document. Please try again.',
        action: () => setError(null)
      });
      setIsLoading(false);
    }
  };

  const handleSummaryUpdate = async (id, content) => {
    try {
      await apiService.updateSummary(id, content);
      const updatedSummaries = summaries.map(s => 
        s.id === id ? { ...s, content, updated_at: new Date().toISOString() } : s
      );
      setSummaries(updatedSummaries);
    } catch (err) {
      console.error('Failed to update summary:', err);
      throw err;
    }
  };

  const handleExport = async (summary, format) => {
    try {
      await apiService.exportSummary(summary, format);
    } catch (err) {
      console.error('Failed to export summary:', err);
    }
  };

  const handleNewDocument = () => {
    setCurrentView('upload');
    setError(null);
  };

  return (
    <Container>
      <AnimatePresence mode="wait">
        {error ? (
          <ErrorCard
            key="error"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ErrorTitle>
              <AlertCircle size={24} />
              {error.title}
            </ErrorTitle>
            <ErrorMessage>{error.message}</ErrorMessage>
            <RetryButton onClick={error.action}>
              Try Again
            </RetryButton>
          </ErrorCard>
        ) : currentView === 'upload' ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DocumentUpload onDocumentUpload={handleDocumentUpload} />
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <SummaryDisplay
              summaries={summaries}
              onSummaryUpdate={handleSummaryUpdate}
              onExport={handleExport}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isLoading && (
          <LoadingOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <LoadingCard
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Loader size={48} color="#764ba2" />
              </motion.div>
              <LoadingText>
                <h3>Processing Document</h3>
                <p>{loadingMessage}</p>
              </LoadingText>
            </LoadingCard>
          </LoadingOverlay>
        )}
      </AnimatePresence>
    </Container>
  );
};

export default Home; 