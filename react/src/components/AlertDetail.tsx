import React from 'react';
import { Alert } from '../types';
import { AlertTriangle, AlertCircle, AlertOctagon, Clock, Shield } from 'lucide-react';

interface AlertDetailProps {
  alert: Alert;
}

export const AlertDetail: React.FC<AlertDetailProps> = ({ alert }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertOctagon className="text-red-500" size={24} />;
      case 'medium':
        return <AlertTriangle className="text-orange-500" size={24} />;
      default:
        return <AlertCircle className="text-yellow-500" size={24} />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const recommendations = {
    high: [
      'Immediately review recent repository activity',
      'Enable branch protection rules',
      'Implement mandatory code review policies',
      'Set up automated security scanning'
    ],
    medium: [
      'Review affected components',
      'Update dependencies to latest secure versions',
      'Document security findings'
    ],
    low: [
      'Monitor for recurring patterns',
      'Update security documentation',
      'Schedule regular security reviews'
    ]
  };

  return (
    <div className="p-6">
      <div className="flex items-start gap-4 mb-6">
        {getSeverityIcon(alert.severity)}
        <div>
          <h2 className="text-xl font-semibold text-gray-900">{alert.title}</h2>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${getSeverityClass(alert.severity)}`}>
            {alert.severity.toUpperCase()} Severity
          </span>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
          <p className="text-gray-900">{alert.description}</p>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Detection Time</h3>
          <div className="flex items-center gap-2 text-gray-700">
            <Clock size={16} />
            <span>{alert.timestamp.toLocaleString()}</span>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Recommended Actions</h3>
          <ul className="space-y-2">
            {recommendations[alert.severity].map((rec, index) => (
              <li key={index} className="flex items-start gap-2">
                <Shield className="text-blue-500 mt-1" size={16} />
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};