import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { 
  TrendingUp, 
  FileText, 
  Clock, 
  Target, 
  Calendar,
  Download,
  Award,
  Activity
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
`;

const StatCard = styled(motion.div)`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-left: 4px solid ${props => props.color || '#764ba2'};
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: ${props => props.color || 'rgba(118, 75, 162, 0.1)'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: ${props => props.iconColor || '#764ba2'};
`;

const StatValue = styled.div`
  font-size: 2.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 8px;
`;

const StatChange = styled.div`
  font-size: 0.8rem;
  color: ${props => props.positive ? '#16a34a' : '#dc2626'};
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ChartsSection = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
`;

const ChartTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FullWidthChart = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
`;

const InsightsSection = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const InsightCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
`;

const InsightTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
`;

const InsightText = styled.p`
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 12px;
`;

const InsightList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const InsightItem = styled.li`
  padding: 8px 0;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:before {
    content: '•';
    color: #764ba2;
    font-weight: bold;
  }
`;

// Color palette for charts
const COLORS = ['#764ba2', '#667eea', '#f093fb', '#f5576c', '#4facfe', '#43e97b'];

const Statistics = () => {
  const [summaries, setSummaries] = useState([]);
  const [timeRange, setTimeRange] = useState('30d'); // '7d', '30d', '90d', 'all'

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    const stored = localStorage.getItem('summaries');
    const data = stored ? JSON.parse(stored) : [];
    setSummaries(data);
  };

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (summaries.length === 0) {
      return {
        total: 0,
        thisWeek: 0,
        avgWords: 0,
        avgConfidence: 0,
        totalProcessingTime: 0,
        successRate: 0
      };
    }

    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thisWeekSummaries = summaries.filter(s => new Date(s.created_at) > weekAgo);
    
    const totalWords = summaries.reduce((sum, s) => sum + (s.stats?.word_count || 0), 0);
    const totalConfidence = summaries.reduce((sum, s) => sum + (s.stats?.confidence_score || 0), 0);
    const successfulSummaries = summaries.filter(s => s.status === 'completed');
    
    return {
      total: summaries.length,
      thisWeek: thisWeekSummaries.length,
      avgWords: Math.round(totalWords / summaries.length),
      avgConfidence: Math.round(totalConfidence / summaries.length),
      totalProcessingTime: summaries.length * 45, // Mock processing time
      successRate: Math.round((successfulSummaries.length / summaries.length) * 100)
    };
  }, [summaries]);

  // Prepare chart data
  const timeSeriesData = React.useMemo(() => {
    const last30Days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toISOString().split('T')[0],
        displayDate: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        summaries: 0,
        words: 0
      };
    });

    summaries.forEach(summary => {
      const summaryDate = new Date(summary.created_at).toISOString().split('T')[0];
      const dayData = last30Days.find(d => d.date === summaryDate);
      if (dayData) {
        dayData.summaries += 1;
        dayData.words += summary.stats?.word_count || 0;
      }
    });

    return last30Days;
  }, [summaries]);

  const templateDistribution = React.useMemo(() => {
    const distribution = {};
    summaries.forEach(summary => {
      const template = summary.template_type;
      distribution[template] = (distribution[template] || 0) + 1;
    });

    return Object.entries(distribution).map(([name, value]) => ({
      name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value,
      percentage: Math.round((value / summaries.length) * 100)
    }));
  }, [summaries]);

  const confidenceData = React.useMemo(() => {
    const ranges = {
      'Very High (90-100%)': 0,
      'High (80-89%)': 0,
      'Medium (70-79%)': 0,
      'Low (60-69%)': 0,
      'Very Low (<60%)': 0
    };

    summaries.forEach(summary => {
      const confidence = summary.stats?.confidence_score || 0;
      if (confidence >= 90) ranges['Very High (90-100%)']++;
      else if (confidence >= 80) ranges['High (80-89%)']++;
      else if (confidence >= 70) ranges['Medium (70-79%)']++;
      else if (confidence >= 60) ranges['Low (60-69%)']++;
      else ranges['Very Low (<60%)']++;
    });

    return Object.entries(ranges).map(([name, value]) => ({
      name,
      value,
      percentage: summaries.length > 0 ? Math.round((value / summaries.length) * 100) : 0
    }));
  }, [summaries]);

  const insights = React.useMemo(() => {
    if (summaries.length === 0) {
      return {
        productivity: "Start creating summaries to see productivity insights.",
        performance: "Upload documents to track performance metrics.",
        recommendations: []
      };
    }

    const recommendations = [];
    
    if (stats.avgConfidence < 80) {
      recommendations.push("Consider using more specific templates for better accuracy");
    }
    
    if (stats.thisWeek < 3) {
      recommendations.push("Try to maintain consistent document processing habits");
    }

    const mostUsedTemplate = templateDistribution.reduce((max, template) => 
      template.value > max.value ? template : max, templateDistribution[0] || { name: 'None', value: 0 });

    return {
      productivity: `You've processed ${stats.total} documents with an average of ${Math.round(stats.total / 4)} per week.`,
      performance: `Your summaries average ${stats.avgConfidence}% confidence with ${stats.avgWords} words per summary.`,
      recommendations: recommendations.length > 0 ? recommendations : ["Great job! Keep up the excellent work."],
      mostUsedTemplate: mostUsedTemplate.name
    };
  }, [summaries, stats, templateDistribution]);

  return (
    <Container>
      <Header>
        <Title>Statistics & Analytics</Title>
        <Subtitle>Track your document processing performance and insights</Subtitle>
      </Header>

      <StatsGrid>
        <StatCard
          color="#667eea"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatIcon color="rgba(102, 126, 234, 0.1)" iconColor="#667eea">
            <FileText size={24} />
          </StatIcon>
          <StatValue>{stats.total}</StatValue>
          <StatLabel>Total Summaries</StatLabel>
          <StatChange positive={stats.thisWeek > 0}>
            <TrendingUp size={12} />
            {stats.thisWeek} this week
          </StatChange>
        </StatCard>

        <StatCard
          color="#16a34a"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <StatIcon color="rgba(22, 163, 74, 0.1)" iconColor="#16a34a">
            <Target size={24} />
          </StatIcon>
          <StatValue>{stats.avgConfidence}%</StatValue>
          <StatLabel>Avg Confidence</StatLabel>
          <StatChange positive={stats.avgConfidence >= 80}>
            <TrendingUp size={12} />
            {stats.avgConfidence >= 80 ? 'Excellent' : 'Good'}
          </StatChange>
        </StatCard>

        <StatCard
          color="#f59e0b"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <StatIcon color="rgba(245, 158, 11, 0.1)" iconColor="#f59e0b">
            <Clock size={24} />
          </StatIcon>
          <StatValue>{stats.avgWords}</StatValue>
          <StatLabel>Avg Words/Summary</StatLabel>
          <StatChange positive={stats.avgWords > 100}>
            <Activity size={12} />
            Optimal length
          </StatChange>
        </StatCard>

        <StatCard
          color="#8b5cf6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <StatIcon color="rgba(139, 92, 246, 0.1)" iconColor="#8b5cf6">
            <Award size={24} />
          </StatIcon>
          <StatValue>{stats.successRate}%</StatValue>
          <StatLabel>Success Rate</StatLabel>
          <StatChange positive={stats.successRate >= 95}>
            <TrendingUp size={12} />
            {stats.successRate >= 95 ? 'Perfect' : 'Good'}
          </StatChange>
        </StatCard>
      </StatsGrid>

      <ChartsSection>
        <ChartCard>
          <ChartTitle>
            <TrendingUp size={20} />
            Daily Activity (Last 30 Days)
          </ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="displayDate" 
                tick={{ fontSize: 12 }}
                stroke="#64748b"
              />
              <YAxis stroke="#64748b" />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="summaries" 
                stroke="#764ba2" 
                strokeWidth={2}
                dot={{ fill: '#764ba2', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <FileText size={20} />
            Template Usage
          </ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={templateDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {templateDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsSection>

      <FullWidthChart>
        <ChartTitle>
          <Target size={20} />
          Confidence Score Distribution
        </ChartTitle>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={confidenceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }}
              stroke="#64748b"
            />
            <YAxis stroke="#64748b" />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px'
              }}
            />
            <Bar dataKey="value" fill="#764ba2" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </FullWidthChart>

      <InsightsSection>
        <InsightCard>
          <InsightTitle>📊 Productivity Insights</InsightTitle>
          <InsightText>{insights.productivity}</InsightText>
          <InsightText>
            Your most used template is <strong>{insights.mostUsedTemplate}</strong>.
          </InsightText>
        </InsightCard>

        <InsightCard>
          <InsightTitle>🎯 Performance Analysis</InsightTitle>
          <InsightText>{insights.performance}</InsightText>
          <InsightText>
            You maintain a {stats.successRate}% success rate across all documents.
          </InsightText>
        </InsightCard>

        <InsightCard>
          <InsightTitle>💡 Recommendations</InsightTitle>
          <InsightList>
            {insights.recommendations.map((rec, index) => (
              <InsightItem key={index}>{rec}</InsightItem>
            ))}
          </InsightList>
        </InsightCard>
      </InsightsSection>
    </Container>
  );
};

export default Statistics; 