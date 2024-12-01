import React from 'react';
import { Repository } from '../types';
import { Shield, ShieldAlert, ShieldOff } from 'lucide-react';

interface RepositoryStatusProps {
  repositories: Repository[];
}

export const RepositoryStatus: React.FC<RepositoryStatusProps> = ({ repositories }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'secure':
        return <Shield className="text-green-500" size={20} />;
      case 'warning':
        return <ShieldAlert className="text-orange-500" size={20} />;
      case 'critical':
        return <ShieldOff className="text-red-500" size={20} />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold mb-4">Repository Status</h2>
      <div className="space-y-3">
        {repositories.map((repo) => (
          <div
            key={repo.name}
            className="flex items-center justify-between p-3 bg-gray-50 rounded"
          >
            <div className="flex items-center gap-2">
              {getStatusIcon(repo.status)}
              <span className="font-medium">{repo.name}</span>
            </div>
            <span className="text-xs text-gray-500">
              Last scan: {repo.lastScan.toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};