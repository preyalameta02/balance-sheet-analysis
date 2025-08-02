import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  CloudArrowUpIcon, 
  DocumentIcon,
  CheckCircleIcon,
  XCircleIcon 
} from '@heroicons/react/24/outline';

const FileUpload = ({ companies, onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        toast.error('Please select a PDF file');
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      toast.error('Please select a PDF file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast.error('Please select a PDF file');
      return;
    }
    
    if (!companyName.trim()) {
      toast.error('Please enter a company name');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('company_name', companyName);

      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('PDF uploaded and processed successfully!');
      setSelectedFile(null);
      setCompanyName('');
      
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload Balance Sheet PDF
        </h2>
        <p className="text-gray-600">
          Upload a PDF file containing balance sheet, profit & loss, or cash flow data.
          The system will automatically extract and process the financial information.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Company Selection */}
        <div>
          <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
            Company Name
          </label>
          <input
            type="text"
            id="company"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter company name (e.g., Jio Platforms)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            required
          />
        </div>

        {/* File Upload Area */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            PDF File
          </label>
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center
              ${dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'}
              ${selectedFile ? 'border-green-500 bg-green-50' : ''}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <div className="space-y-4">
              {selectedFile ? (
                <div className="flex items-center justify-center space-x-2">
                  <CheckCircleIcon className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Drop your PDF here, or click to browse
                    </p>
                    <p className="text-xs text-gray-500">
                      Only PDF files are supported
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Upload Button */}
        <div>
          <button
            type="submit"
            disabled={!selectedFile || !companyName.trim() || uploading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Upload and Process PDF'
            )}
          </button>
        </div>
      </form>

      {/* Existing Companies */}
      {companies.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Available Companies
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company) => (
              <div
                key={company.id}
                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
              >
                <DocumentIcon className="h-5 w-5 text-gray-400" />
                <span className="text-sm font-medium text-gray-900">
                  {company.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 