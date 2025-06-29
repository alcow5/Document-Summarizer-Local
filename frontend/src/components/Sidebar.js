import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FileText, 
  History, 
  BarChart3, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  Shield,
  Home
} from 'lucide-react';

const SidebarContainer = styled(motion.aside)`
  width: ${props => props.collapsed ? '60px' : '240px'};
  background: #1e293b;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  position: relative;
`;

const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 1.1rem;
`;

const CollapseButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background-color 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const Navigation = styled.nav`
  flex: 1;
  padding: 20px 0;
`;

const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
  border-left: 3px solid transparent;

  ${props => props.active && `
    background: rgba(124, 63, 162, 0.2);
    border-left-color: #764ba2;
    
    &::before {
      content: '';
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: #764ba2;
    }
  `}

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(2px);
  }

  .icon {
    min-width: 20px;
  }

  .label {
    opacity: ${props => props.collapsed ? 0 : 1};
    transition: opacity 0.3s ease;
    white-space: nowrap;
  }
`;

const SidebarFooter = styled.div`
  padding: 20px;
  border-top: 1px solid #334155;
`;

const PrivacyBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 6px;
  font-size: 0.8rem;
  color: #22c55e;

  .text {
    opacity: ${props => props.collapsed ? 0 : 1};
    transition: opacity 0.3s ease;
  }
`;

const navItems = [
  {
    path: '/',
    icon: Home,
    label: 'Summarize',
    exact: true
  },
  {
    path: '/history',
    icon: History,
    label: 'History'
  },
  {
    path: '/stats',
    icon: BarChart3,
    label: 'Statistics'
  },
  {
    path: '/settings',
    icon: Settings,
    label: 'Settings'
  }
];

const Sidebar = ({ collapsed, onToggle }) => {
  const location = useLocation();

  const isActive = (path, exact = false) => {
    if (exact) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <SidebarContainer
      collapsed={collapsed}
      initial={{ width: collapsed ? 60 : 240 }}
      animate={{ width: collapsed ? 60 : 240 }}
      transition={{ duration: 0.3 }}
    >
      <SidebarHeader>
        {!collapsed && (
          <Logo>
            <Shield size={24} />
            <span>DocSum</span>
          </Logo>
        )}
        
        <CollapseButton onClick={onToggle}>
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </CollapseButton>
      </SidebarHeader>

      <Navigation>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path, item.exact);
          
          return (
            <NavItem
              key={item.path}
              to={item.path}
              active={active}
              collapsed={collapsed}
            >
              <Icon size={20} className="icon" />
              <span className="label">{item.label}</span>
            </NavItem>
          );
        })}
      </Navigation>

      <SidebarFooter>
        <PrivacyBadge collapsed={collapsed}>
          <Shield size={16} />
          <span className="text">100% Local</span>
        </PrivacyBadge>
      </SidebarFooter>
    </SidebarContainer>
  );
};

export default Sidebar; 