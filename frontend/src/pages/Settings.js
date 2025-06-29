import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  Shield, 
  Palette, 
  Database,
  Download,
  Upload,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Info,
  Monitor,
  Moon,
  Sun
} from 'lucide-react';

const Container = styled.div`
  max-width: 800px;
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

const SettingsCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  overflow: hidden;
`;

const CardHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
`;

const CardTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CardDescription = styled.p`
  color: #64748b;
  font-size: 0.9rem;
`;

const CardContent = styled.div`
  padding: 24px;
`;

const SettingGroup = styled.div`
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const SettingLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
  cursor: pointer;
`;

const SettingDescription = styled.p`
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 12px;
  padding-left: 24px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #764ba2;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #764ba2;
  }
`;

const Switch = styled.div`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
`;

const SwitchInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
`;

const SwitchSlider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${props => props.checked ? '#764ba2' : '#e2e8f0'};
  transition: .4s;
  border-radius: 24px;

  &:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: ${props => props.checked ? '28px' : '4px'};
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
`;

const Button = styled(motion.button)`
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
  ` : `
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    
    &:hover {
      border-color: #cbd5e1;
      color: #475569;
    }
  `}

  ${props => props.danger && `
    background: #ef4444;
    color: white;
    
    &:hover {
      background: #dc2626;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
    }
  `}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }
`;

const AlertBox = styled.div`
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return `
          background: rgba(34, 197, 94, 0.1);
          border: 1px solid rgba(34, 197, 94, 0.2);
          color: #16a34a;
        `;
      case 'warning':
        return `
          background: rgba(251, 191, 36, 0.1);
          border: 1px solid rgba(251, 191, 36, 0.2);
          color: #d97706;
        `;
      case 'error':
        return `
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          color: #dc2626;
        `;
      default:
        return `
          background: rgba(59, 130, 246, 0.1);
          border: 1px solid rgba(59, 130, 246, 0.2);
          color: #2563eb;
        `;
    }
  }}
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
  margin: 12px 0;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: ${props => props.percent}%;
  transition: width 0.3s ease;
`;

const StorageInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const StorageItem = styled.div`
  text-align: center;
  
  .value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }
  
  .label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

const Settings = () => {
  const [settings, setSettings] = useState({
    // General
    autoSave: true,
    defaultTemplate: 'general',
    maxFileSize: '50',
    language: 'en',
    
    // Appearance
    theme: 'light',
    fontSize: 'medium',
    compactMode: false,
    
    // Privacy & Security
    encryptData: true,
    autoDeleteOlder: false,
    deleteAfterDays: '30',
    
    // Advanced
    debugMode: false,
    betaFeatures: false,
    analyticsEnabled: true
  });

  const [notification, setNotification] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [storageUsage, setStorageUsage] = useState({
    used: 12.5,
    total: 100,
    summaries: 45,
    documents: 12
  });

  useEffect(() => {
    loadSettings();
    calculateStorageUsage();
  }, []);

  const loadSettings = () => {
    const stored = localStorage.getItem('app_settings');
    if (stored) {
      setSettings({ ...settings, ...JSON.parse(stored) });
    }
  };

  const calculateStorageUsage = () => {
    const summaries = JSON.parse(localStorage.getItem('summaries') || '[]');
    const used = JSON.stringify(summaries).length / 1024 / 1024; // MB
    
    setStorageUsage({
      used: Math.round(used * 100) / 100,
      total: 100,
      summaries: summaries.length,
      documents: summaries.length
    });
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      localStorage.setItem('app_settings', JSON.stringify(settings));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      showNotification('Settings saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save settings', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      const defaultSettings = {
        autoSave: true,
        defaultTemplate: 'general',
        maxFileSize: '50',
        language: 'en',
        theme: 'light',
        fontSize: 'medium',
        compactMode: false,
        encryptData: true,
        autoDeleteOlder: false,
        deleteAfterDays: '30',
        debugMode: false,
        betaFeatures: false,
        analyticsEnabled: true
      };
      setSettings(defaultSettings);
      showNotification('Settings reset to default values', 'info');
    }
  };

  const handleExportData = () => {
    const summaries = JSON.parse(localStorage.getItem('summaries') || '[]');
    const data = {
      summaries,
      settings,
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `document_summarizer_backup_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Data exported successfully!', 'success');
  };

  const handleClearData = () => {
    if (window.confirm('Are you sure you want to delete all summaries? This action cannot be undone.')) {
      localStorage.removeItem('summaries');
      calculateStorageUsage();
      showNotification('All data cleared successfully', 'warning');
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const usagePercent = (storageUsage.used / storageUsage.total) * 100;

  return (
    <Container>
      <Header>
        <Title>Settings</Title>
        <Subtitle>Customize your document summarizer experience</Subtitle>
      </Header>

      {notification && (
        <AlertBox type={notification.type}>
          {notification.type === 'success' && <CheckCircle size={20} />}
          {notification.type === 'warning' && <AlertTriangle size={20} />}
          {notification.type === 'error' && <AlertTriangle size={20} />}
          {notification.type === 'info' && <Info size={20} />}
          {notification.message}
        </AlertBox>
      )}

      <SettingsCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <CardHeader>
          <CardTitle>
            <SettingsIcon size={20} />
            General Settings
          </CardTitle>
          <CardDescription>
            Configure basic application behavior and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SettingGroup>
            <SettingLabel>
              <Switch>
                <SwitchInput
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                />
                <SwitchSlider checked={settings.autoSave} />
              </Switch>
              Auto-save summaries
            </SettingLabel>
            <SettingDescription>
              Automatically save summaries as they are generated
            </SettingDescription>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Default Template</SettingLabel>
            <Select
              value={settings.defaultTemplate}
              onChange={(e) => handleSettingChange('defaultTemplate', e.target.value)}
            >
              <option value="general">General Summary</option>
              <option value="customer_feedback">Customer Feedback</option>
              <option value="contract_analysis">Contract Analysis</option>
            </Select>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Maximum File Size (MB)</SettingLabel>
            <Input
              type="number"
              value={settings.maxFileSize}
              onChange={(e) => handleSettingChange('maxFileSize', e.target.value)}
              min="1"
              max="100"
            />
          </SettingGroup>
        </CardContent>
      </SettingsCard>

      <SettingsCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <CardHeader>
          <CardTitle>
            <Palette size={20} />
            Appearance
          </CardTitle>
          <CardDescription>
            Customize the look and feel of the application
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SettingGroup>
            <SettingLabel>Theme</SettingLabel>
            <Select
              value={settings.theme}
              onChange={(e) => handleSettingChange('theme', e.target.value)}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </Select>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Font Size</SettingLabel>
            <Select
              value={settings.fontSize}
              onChange={(e) => handleSettingChange('fontSize', e.target.value)}
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </Select>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>
              <Switch>
                <SwitchInput
                  type="checkbox"
                  checked={settings.compactMode}
                  onChange={(e) => handleSettingChange('compactMode', e.target.checked)}
                />
                <SwitchSlider checked={settings.compactMode} />
              </Switch>
              Compact Mode
            </SettingLabel>
            <SettingDescription>
              Use a more condensed layout to show more content
            </SettingDescription>
          </SettingGroup>
        </CardContent>
      </SettingsCard>

      <SettingsCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <CardHeader>
          <CardTitle>
            <Shield size={20} />
            Privacy & Security
          </CardTitle>
          <CardDescription>
            Control how your data is stored and protected
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SettingGroup>
            <SettingLabel>
              <Switch>
                <SwitchInput
                  type="checkbox"
                  checked={settings.encryptData}
                  onChange={(e) => handleSettingChange('encryptData', e.target.checked)}
                />
                <SwitchSlider checked={settings.encryptData} />
              </Switch>
              Encrypt Local Data
            </SettingLabel>
            <SettingDescription>
              Encrypt summaries and documents stored locally
            </SettingDescription>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>
              <Switch>
                <SwitchInput
                  type="checkbox"
                  checked={settings.autoDeleteOlder}
                  onChange={(e) => handleSettingChange('autoDeleteOlder', e.target.checked)}
                />
                <SwitchSlider checked={settings.autoDeleteOlder} />
              </Switch>
              Auto-delete Old Summaries
            </SettingLabel>
            {settings.autoDeleteOlder && (
              <Input
                type="number"
                value={settings.deleteAfterDays}
                onChange={(e) => handleSettingChange('deleteAfterDays', e.target.value)}
                placeholder="Days to keep summaries"
                min="1"
                max="365"
                style={{ marginTop: '8px' }}
              />
            )}
          </SettingGroup>
        </CardContent>
      </SettingsCard>

      <SettingsCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <CardHeader>
          <CardTitle>
            <Database size={20} />
            Data Management
          </CardTitle>
          <CardDescription>
            Manage your stored data and storage usage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Storage Used</span>
              <span>{storageUsage.used} MB / {storageUsage.total} MB</span>
            </div>
            <ProgressBar>
              <ProgressFill percent={usagePercent} />
            </ProgressBar>
          </div>

          <StorageInfo>
            <StorageItem>
              <div className="value">{storageUsage.summaries}</div>
              <div className="label">Summaries</div>
            </StorageItem>
            <StorageItem>
              <div className="value">{storageUsage.documents}</div>
              <div className="label">Documents</div>
            </StorageItem>
            <StorageItem>
              <div className="value">{Math.round(usagePercent)}%</div>
              <div className="label">Usage</div>
            </StorageItem>
          </StorageInfo>

          <ButtonGroup style={{ marginTop: '20px' }}>
            <Button onClick={handleExportData}>
              <Download size={16} />
              Export Data
            </Button>
            <Button danger onClick={handleClearData}>
              <Trash2 size={16} />
              Clear All Data
            </Button>
          </ButtonGroup>
        </CardContent>
      </SettingsCard>

      <ButtonGroup>
        <Button onClick={handleReset}>
          <RefreshCw size={16} />
          Reset to Defaults
        </Button>
        <Button primary onClick={handleSave} disabled={isSaving}>
          {isSaving ? <RefreshCw size={16} className="animate-spin" /> : <Save size={16} />}
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </ButtonGroup>
    </Container>
  );
};

export default Settings; 