import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Copy, 
  Edit3, 
  Save, 
  X, 
  Share,
  Clock,
  CheckCircle,
  AlertCircle,
  MoreVertical,
  Printer,
  Star,
  Archive
} from 'lucide-react';

const Container = styled(motion.div)`
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
`;

const SummaryCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 24px;
`;

const SummaryHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
`;

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const DocumentInfo = styled.div`
  flex: 1;
`;

const DocumentTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DocumentMeta = styled.div`
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

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled(motion.button)`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;

  &:hover {
    border-color: #764ba2;
    color: #764ba2;
    transform: translateY(-1px);
  }

  &.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-color: transparent;

    &:hover {
      color: white;
      box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
    }
  }
`;

const SummaryContent = styled.div`
  padding: 24px;
`;

const SummaryText = styled.div`
  font-size: 1rem;
  line-height: 1.7;
  color: #374151;
  white-space: pre-wrap;
  
  h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #f1f5f9;
  }

  h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 16px 0 8px 0;
  }

  ul, ol {
    margin: 12px 0;
    padding-left: 24px;
  }

  li {
    margin: 6px 0;
  }

  strong {
    font-weight: 600;
    color: #1e293b;
  }

  p {
    margin: 12px 0;
  }
`;

const EditableText = styled.textarea`
  width: 100%;
  min-height: 400px;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.7;
  font-family: inherit;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: #764ba2;
  }
`;

const EditActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
`;

const StatsSection = styled.div`
  padding: 20px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
`;

const StatItem = styled.div`
  text-align: center;
  
  .value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
  }
  
  .label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  
  ${props => {
    switch (props.status) {
      case 'completed':
        return `
          background: rgba(34, 197, 94, 0.1);
          color: #16a34a;
          border: 1px solid rgba(34, 197, 94, 0.2);
        `;
      case 'processing':
        return `
          background: rgba(251, 191, 36, 0.1);
          color: #d97706;
          border: 1px solid rgba(251, 191, 36, 0.2);
        `;
      case 'error':
        return `
          background: rgba(239, 68, 68, 0.1);
          color: #dc2626;
          border: 1px solid rgba(239, 68, 68, 0.2);
        `;
      default:
        return `
          background: rgba(107, 114, 128, 0.1);
          color: #6b7280;
          border: 1px solid rgba(107, 114, 128, 0.2);
        `;
    }
  }}
`;

const Toast = styled(motion.div)`
  position: fixed;
  top: 20px;
  right: 20px;
  background: #16a34a;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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

const SummaryDisplay = ({ summaries, onSummaryUpdate, onExport }) => {
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const showNotification = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleEdit = (summary) => {
    setEditingId(summary.id);
    setEditText(summary.content);
  };

  const handleSave = async () => {
    try {
      await onSummaryUpdate(editingId, editText);
      setEditingId(null);
      setEditText('');
      showNotification('Summary updated successfully!');
    } catch (error) {
      showNotification('Failed to update summary');
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditText('');
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      showNotification('Summary copied to clipboard!');
    } catch (error) {
      showNotification('Failed to copy to clipboard');
    }
  };

  const handleExport = (summary, format) => {
    onExport(summary, format);
    showNotification(`Summary exported as ${format.toUpperCase()}!`);
  };

  if (!summaries || summaries.length === 0) {
    return (
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', padding: '60px 20px' }}
        >
          <FileText size={64} color="#94a3b8" style={{ marginBottom: '16px' }} />
          <h3 style={{ color: '#64748b', marginBottom: '8px' }}>No summaries yet</h3>
          <p style={{ color: '#94a3b8' }}>Upload a document to get started</p>
        </motion.div>
      </Container>
    );
  }

  return (
    <Container>
      <AnimatePresence>
        {summaries.map((summary, index) => (
          <SummaryCard
            key={summary.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <SummaryHeader>
              <HeaderTop>
                <DocumentInfo>
                  <DocumentTitle>
                    <FileText size={20} />
                    {summary.filename}
                  </DocumentTitle>
                  <DocumentMeta>
                    <MetaItem>
                      <Clock size={14} />
                      {formatDate(summary.created_at)}
                    </MetaItem>
                    <TemplateTag>{summary.template_type}</TemplateTag>
                    <StatusBadge status={summary.status}>
                      {summary.status === 'completed' && <CheckCircle size={14} />}
                      {summary.status === 'error' && <AlertCircle size={14} />}
                      {summary.status}
                    </StatusBadge>
                  </DocumentMeta>
                </DocumentInfo>

                <ActionButtons>
                  <ActionButton
                    onClick={() => handleCopy(summary.content)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Copy size={16} />
                    Copy
                  </ActionButton>
                  
                  <ActionButton
                    onClick={() => handleEdit(summary)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Edit3 size={16} />
                    Edit
                  </ActionButton>
                  
                  <ActionButton
                    className="primary"
                    onClick={() => handleExport(summary, 'pdf')}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Download size={16} />
                    Export
                  </ActionButton>
                </ActionButtons>
              </HeaderTop>
            </SummaryHeader>

            <SummaryContent>
              {editingId === summary.id ? (
                <>
                  <EditableText
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    placeholder="Edit your summary..."
                  />
                  <EditActions>
                    <ActionButton onClick={handleCancel}>
                      <X size={16} />
                      Cancel
                    </ActionButton>
                    <ActionButton className="primary" onClick={handleSave}>
                      <Save size={16} />
                      Save Changes
                    </ActionButton>
                  </EditActions>
                </>
              ) : (
                <SummaryText
                  dangerouslySetInnerHTML={{ __html: summary.content }}
                />
              )}
            </SummaryContent>

            {summary.stats && (
              <StatsSection>
                <StatsGrid>
                  <StatItem>
                    <div className="value">{summary.stats.word_count || 0}</div>
                    <div className="label">Words</div>
                  </StatItem>
                  <StatItem>
                    <div className="value">{summary.stats.reading_time || 0}m</div>
                    <div className="label">Read Time</div>
                  </StatItem>
                  <StatItem>
                    <div className="value">{summary.stats.compression_ratio || 0}%</div>
                    <div className="label">Compression</div>
                  </StatItem>
                  <StatItem>
                    <div className="value">{summary.stats.confidence_score || 0}%</div>
                    <div className="label">Confidence</div>
                  </StatItem>
                </StatsGrid>
              </StatsSection>
            )}
          </SummaryCard>
        ))}
      </AnimatePresence>

      <AnimatePresence>
        {showToast && (
          <Toast
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
          >
            <CheckCircle size={16} />
            {toastMessage}
          </Toast>
        )}
      </AnimatePresence>
    </Container>
  );
};

export default SummaryDisplay; 