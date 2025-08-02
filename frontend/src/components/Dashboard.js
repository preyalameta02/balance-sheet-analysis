import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import FileUpload from './FileUpload';
import DataVisualization from './DataVisualization';
import ChatInterface from './ChatInterface';
import { 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon, 
  DocumentArrowUpIcon 
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');
  const [companies, setCompanies] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCompanies();
    fetchMetrics();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get('/companies');
      setCompanies(response.data);
    } catch (error) {
      console.error('Error fetching companies:', error);
      toast.error('Failed to fetch companies');
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      toast.error('Failed to fetch metrics');
    }
  };

  const tabs = [
    {
      id: 'upload',
      name: 'Upload PDF',
      icon: DocumentArrowUpIcon,
      description: 'Upload and process balance sheet PDFs'
    },
    {
      id: 'visualize',
      name: 'Data Visualization',
      icon: ChartBarIcon,
      description: 'View financial data and charts'
    },
    {
      id: 'chat',
      name: 'AI Chat',
      icon: ChatBubbleLeftRightIcon,
      description: 'Ask questions about financial data'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.email}
        </h1>
        <p className="mt-2 text-gray-600">
          Role: {user?.role} | Access Level: {
            user?.role === 'ambani_family' ? 'All Companies' :
            user?.role === 'ceo' ? 'Company CEO' : 'Analyst'
          }
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow">
        {activeTab === 'upload' && (
          <FileUpload 
            companies={companies}
            onUploadSuccess={fetchCompanies}
          />
        )}
        
        {activeTab === 'visualize' && (
          <DataVisualization 
            companies={companies}
            metrics={metrics}
          />
        )}
        
        {activeTab === 'chat' && (
          <ChatInterface 
            companies={companies}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard; 