import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Calendar, 
  FileText, 
  Download, 
  Trash2,
  Eye,
  Clock,
  SortDesc,
  SortAsc
} from 'lucide-react';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const Header = styled.div`
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: #64748b;
  font-size: 1.1rem;
`;

const Controls = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
`;

const SearchBox = styled.div`
  position: relative;
  flex: 1;
  min-width: 300px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #764ba2;
  }
  
  &::placeholder {
    color: #94a3b8;
  }
`;

const SearchIcon = styled(Search)`
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
`;

const FilterButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #64748b;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #764ba2;
    color: #764ba2;
  }
  
  &.active {
    border-color: #764ba2;
    background: rgba(118, 75, 162, 0.1);
    color: #764ba2;
  }
`;

const SortButton = styled(FilterButton)``;

const StatsRow = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
`;

const StatCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 4px;
  }
  
  .label {
    font-size: 0.9rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

const HistoryGrid = styled.div`
  display: grid;
  gap: 16px;
`;

const HistoryItem = styled(motion.div)`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }
`;

const ItemHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const ItemInfo = styled.div`
  flex: 1;
`;

const ItemTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ItemMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.9rem;
  color: #64748b;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const TemplateTag = styled.span`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const ItemActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #764ba2;
    color: #764ba2;
  }
  
  &.danger:hover {
    border-color: #ef4444;
    color: #ef4444;
  }
`;

const ItemPreview = styled.div`
  padding: 20px;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #374151;
  
  .preview-text {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
  
  .icon {
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  h3 {
    font-size: 1.2rem;
    margin-bottom: 8px;
  }
  
  p {
    color: #94a3b8;
  }
`;

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getPreviewText = (content) => {
  // Strip markdown and HTML, take first 200 characters
  const plainText = content.replace(/[#*_`]/g, '').replace(/<[^>]*>/g, '');
  return plainText.length > 200 ? plainText.substring(0, 200) + '...' : plainText;
};

const History = () => {
  const [summaries, setSummaries] = useState([]);
  const [filteredSummaries, setFilteredSummaries] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date'); // 'date', 'name', 'template'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  const [filterTemplate, setFilterTemplate] = useState('all');

  useEffect(() => {
    loadSummaries();
  }, []);

  useEffect(() => {
    filterAndSortSummaries();
  }, [summaries, searchTerm, sortBy, sortOrder, filterTemplate]);

  const loadSummaries = () => {
    const stored = localStorage.getItem('summaries');
    const data = stored ? JSON.parse(stored) : [];
    setSummaries(data);
  };

  const filterAndSortSummaries = () => {
    let filtered = [...summaries];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(summary =>
        summary.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        summary.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply template filter
    if (filterTemplate !== 'all') {
      filtered = filtered.filter(summary => summary.template_type === filterTemplate);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.filename.toLowerCase();
          bValue = b.filename.toLowerCase();
          break;
        case 'template':
          aValue = a.template_type;
          bValue = b.template_type;
          break;
        case 'date':
        default:
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredSummaries(filtered);
  };

  const handleView = (summary) => {
    // Navigate to summary view or open modal
    console.log('View summary:', summary);
  };

  const handleDelete = (summaryId) => {
    const updatedSummaries = summaries.filter(s => s.id !== summaryId);
    setSummaries(updatedSummaries);
    localStorage.setItem('summaries', JSON.stringify(updatedSummaries));
  };

  const handleExport = (summary) => {
    // Simple text export for demo
    const blob = new Blob([summary.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${summary.filename}_summary.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const uniqueTemplates = [...new Set(summaries.map(s => s.template_type))];

  const stats = {
    total: summaries.length,
    thisWeek: summaries.filter(s => {
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      return new Date(s.created_at) > weekAgo;
    }).length,
    totalWords: summaries.reduce((sum, s) => sum + (s.stats?.word_count || 0), 0),
    avgConfidence: summaries.length > 0 
      ? Math.round(summaries.reduce((sum, s) => sum + (s.stats?.confidence_score || 0), 0) / summaries.length)
      : 0
  };

  return (
    <Container>
      <Header>
        <Title>Summary History</Title>
        <Subtitle>Browse and manage your document summaries</Subtitle>
      </Header>

      <StatsRow>
        <StatCard>
          <div className="value">{stats.total}</div>
          <div className="label">Total Summaries</div>
        </StatCard>
        <StatCard>
          <div className="value">{stats.thisWeek}</div>
          <div className="label">This Week</div>
        </StatCard>
        <StatCard>
          <div className="value">{stats.totalWords.toLocaleString()}</div>
          <div className="label">Total Words</div>
        </StatCard>
        <StatCard>
          <div className="value">{stats.avgConfidence}%</div>
          <div className="label">Avg Confidence</div>
        </StatCard>
      </StatsRow>

      <Controls>
        <SearchBox>
          <SearchIcon size={20} />
          <SearchInput
            type="text"
            placeholder="Search summaries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </SearchBox>

        <FilterButton
          className={filterTemplate === 'all' ? 'active' : ''}
          onClick={() => setFilterTemplate('all')}
        >
          <Filter size={16} />
          All Templates
        </FilterButton>

        {uniqueTemplates.map(template => (
          <FilterButton
            key={template}
            className={filterTemplate === template ? 'active' : ''}
            onClick={() => setFilterTemplate(template)}
          >
            {template}
          </FilterButton>
        ))}

        <SortButton onClick={() => toggleSort('date')}>
          {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
          Date
        </SortButton>

        <SortButton onClick={() => toggleSort('name')}>
          {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
          Name
        </SortButton>
      </Controls>

      {filteredSummaries.length === 0 ? (
        <EmptyState>
          <div className="icon">
            <FileText size={64} />
          </div>
          <h3>No summaries found</h3>
          <p>
            {summaries.length === 0 
              ? 'Upload your first document to get started'
              : 'Try adjusting your search or filters'
            }
          </p>
        </EmptyState>
      ) : (
        <HistoryGrid>
          <AnimatePresence>
            {filteredSummaries.map((summary, index) => (
              <HistoryItem
                key={summary.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => handleView(summary)}
              >
                <ItemHeader>
                  <ItemInfo>
                    <ItemTitle>
                      <FileText size={20} />
                      {summary.filename}
                    </ItemTitle>
                    <ItemMeta>
                      <MetaItem>
                        <Clock size={14} />
                        {formatDate(summary.created_at)}
                      </MetaItem>
                      <TemplateTag>{summary.template_type}</TemplateTag>
                      {summary.stats && (
                        <MetaItem>
                          {summary.stats.word_count} words
                        </MetaItem>
                      )}
                    </ItemMeta>
                  </ItemInfo>
                  
                  <ItemActions onClick={(e) => e.stopPropagation()}>
                    <ActionButton
                      onClick={() => handleView(summary)}
                      title="View Summary"
                    >
                      <Eye size={16} />
                    </ActionButton>
                    <ActionButton
                      onClick={() => handleExport(summary)}
                      title="Export Summary"
                    >
                      <Download size={16} />
                    </ActionButton>
                    <ActionButton
                      className="danger"
                      onClick={() => handleDelete(summary.id)}
                      title="Delete Summary"
                    >
                      <Trash2 size={16} />
                    </ActionButton>
                  </ItemActions>
                </ItemHeader>
                
                <ItemPreview>
                  <div className="preview-text">
                    {getPreviewText(summary.content)}
                  </div>
                </ItemPreview>
              </HistoryItem>
            ))}
          </AnimatePresence>
        </HistoryGrid>
      )}
    </Container>
  );
};

export default History; 