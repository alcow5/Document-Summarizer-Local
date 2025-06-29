import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  File, 
  Check, 
  AlertCircle,
  Loader,
  ChevronDown,
  Sparkles
} from 'lucide-react';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const WelcomeSection = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: #64748b;
  margin-bottom: 8px;
`;

const PrivacyNote = styled.p`
  font-size: 0.9rem;
  color: #22c55e;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
`;

const UploadSection = styled.div`
  margin-bottom: 32px;
`;

const DropzoneContainer = styled(motion.div)`
  border: 2px dashed ${props => props.isDragActive ? '#764ba2' : '#cbd5e1'};
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  background: ${props => props.isDragActive ? 'rgba(118, 75, 162, 0.05)' : '#f8fafc'};
  transition: all 0.3s ease;
  margin-bottom: 24px;

  &:hover {
    border-color: #764ba2;
    background: rgba(118, 75, 162, 0.02);
  }
`;

const UploadIcon = styled(motion.div)`
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
  color: ${props => props.isDragActive ? '#764ba2' : '#64748b'};
`;

const UploadText = styled.div`
  h3 {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
  }

  p {
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 4px;
  }

  .formats {
    font-size: 0.9rem;
    color: #94a3b8;
  }
`;

const TemplateSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TemplateGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
`;

const TemplateCard = styled(motion.div)`
  padding: 20px;
  border: 2px solid ${props => props.selected ? '#764ba2' : '#e2e8f0'};
  border-radius: 8px;
  cursor: pointer;
  background: ${props => props.selected ? 'rgba(118, 75, 162, 0.05)' : 'white'};
  transition: all 0.2s ease;

  &:hover {
    border-color: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  p {
    font-size: 0.9rem;
    color: #64748b;
    line-height: 1.4;
  }
`;

const CustomPromptSection = styled(motion.div)`
  margin-top: 16px;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #764ba2;
  }

  &::placeholder {
    color: #94a3b8;
  }
`;

const ActionSection = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
`;

const ActionButton = styled(motion.button)`
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;

  ${props => props.primary ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(118, 75, 162, 0.3);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
  ` : `
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    
    &:hover {
      border-color: #cbd5e1;
      color: #475569;
    }
  `}
`;

const templates = [
  {
    id: 'general',
    name: 'General Summary',
    description: 'Create a comprehensive summary highlighting key points and main themes.',
    icon: FileText
  },
  {
    id: 'customer_feedback',
    name: 'Customer Feedback',
    description: 'Analyze customer feedback with sentiment analysis and actionable insights.',
    icon: Sparkles
  },
  {
    id: 'contract_analysis',
    name: 'Contract Analysis',
    description: 'Extract key terms, obligations, and important dates from contracts.',
    icon: File
  }
];

const DocumentUpload = ({ onDocumentUpload }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('general');
  const [customPrompt, setCustomPrompt] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  const handleProcess = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    try {
      await onDocumentUpload(selectedFile, selectedTemplate, customPrompt || null);
    } catch (error) {
      console.error('Document processing failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setSelectedTemplate('general');
    setCustomPrompt('');
    setIsProcessing(false);
  };

  return (
    <Container>
      <WelcomeSection>
        <Title>
          <FileText size={40} />
          Document Summarizer
        </Title>
        <Subtitle>
          Upload your documents and get AI-powered summaries instantly
        </Subtitle>
        <PrivacyNote>
          <Check size={16} />
          100% private - all processing happens locally on your device
        </PrivacyNote>
      </WelcomeSection>

      <UploadSection>
        <DropzoneContainer
          {...getRootProps()}
          isDragActive={isDragActive}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <input {...getInputProps()} />
          <UploadIcon
            isDragActive={isDragActive}
            animate={{ y: isDragActive ? -5 : 0 }}
          >
            <Upload size={48} />
          </UploadIcon>
          <UploadText>
            {selectedFile ? (
              <>
                <h3>✓ {selectedFile.name}</h3>
                <p>File selected • Click to change</p>
                <p className="formats">
                  {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
                </p>
              </>
            ) : (
              <>
                <h3>
                  {isDragActive ? 'Drop your document here' : 'Drag & drop your document'}
                </h3>
                <p>or click to browse files</p>
                <p className="formats">Supports PDF and DOCX files (max 50MB)</p>
              </>
            )}
          </UploadText>
        </DropzoneContainer>
      </UploadSection>

      <TemplateSection>
        <SectionTitle>
          <Sparkles size={20} />
          Choose Summary Template
        </SectionTitle>
        
        <TemplateGrid>
          {templates.map((template) => {
            const Icon = template.icon;
            return (
              <TemplateCard
                key={template.id}
                selected={selectedTemplate === template.id}
                onClick={() => setSelectedTemplate(template.id)}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <h4>
                  <Icon size={20} />
                  {template.name}
                </h4>
                <p>{template.description}</p>
              </TemplateCard>
            );
          })}
        </TemplateGrid>

        <AnimatePresence>
          {selectedTemplate === 'custom' && (
            <CustomPromptSection
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <TextArea
                placeholder="Enter your custom summarization prompt..."
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
              />
            </CustomPromptSection>
          )}
        </AnimatePresence>
      </TemplateSection>

      <ActionSection>
        {selectedFile && (
          <ActionButton onClick={resetForm}>
            Clear
          </ActionButton>
        )}
        
        <ActionButton
          primary
          disabled={!selectedFile || isProcessing}
          onClick={handleProcess}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isProcessing ? (
            <>
              <Loader size={20} className="animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              Summarize Document
            </>
          )}
        </ActionButton>
      </ActionSection>
    </Container>
  );
};

export default DocumentUpload; 