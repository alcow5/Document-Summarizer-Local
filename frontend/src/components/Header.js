import React from 'react';
import styled from 'styled-components';
import { FileText, Plus, Settings, Activity } from 'lucide-react';

const HeaderContainer = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const AppTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CurrentDocument = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  opacity: 0.9;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  animation: pulse 2s infinite;

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const Header = ({ currentDocument, onNewDocument }) => {
  return (
    <HeaderContainer>
      <LeftSection>
        <AppTitle>
          <FileText size={24} />
          Document Summarizer
        </AppTitle>
        
        {currentDocument && (
          <CurrentDocument>
            <FileText size={16} />
            <span>{currentDocument.filename}</span>
            <span style={{ opacity: 0.7 }}>
              • {currentDocument.template}
            </span>
          </CurrentDocument>
        )}
      </LeftSection>

      <RightSection>
        <StatusIndicator>
          <StatusDot />
          <span>Privacy Mode: Local Only</span>
        </StatusIndicator>

        <ActionButton onClick={onNewDocument}>
          <Plus size={16} />
          New Summary
        </ActionButton>

        <ActionButton onClick={() => console.log('Settings clicked')}>
          <Settings size={16} />
          Settings
        </ActionButton>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header; 