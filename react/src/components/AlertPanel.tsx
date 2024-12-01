import React, { useState } from 'react';
import { Alert } from '../types';
import { AlertTriangle, AlertCircle, AlertOctagon, GitCommit, Clock, Shield } from 'lucide-react';
import { Modal } from './Model';
import { AlertDetail } from './AlertDetail';

interface Commit {
  repo: string;
  pusher: string;
  message: string;
  timestamp: string;
  isUnusual?: boolean;
  isVulnerable?: boolean;
}

interface AlertPanelProps {
  alerts: Alert[];
  latestCommit: Commit | null;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, latestCommit }) => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertOctagon className="text-red-500" size={20} />;
      case 'medium':
        return <AlertTriangle className="text-orange-500" size={20} />;
      default:
        return <AlertCircle className="text-yellow-500" size={20} />;
    }
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Security Alerts</h2>
        <div className="space-y-3">
          {latestCommit && (
            <div className={`border-l-4 ${latestCommit.isUnusual || latestCommit.isVulnerable ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'} p-3 rounded`}>
              <div className="flex items-center gap-2">
                <GitCommit className={latestCommit.isUnusual || latestCommit.isVulnerable ? 'text-red-500' : 'text-blue-500'} size={20} />
                <h3 className="font-medium">
                  {latestCommit.isVulnerable ? 'Vulnerable Commit Detected' : latestCommit.isUnusual ? 'Unusual Commit Detected' : 'Latest Commit'}
                </h3>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {latestCommit.message} in {latestCommit.repo} by {latestCommit.pusher}
              </p>
              <span className="text-xs text-gray-500 mt-2 block">
                {new Date(latestCommit.timestamp).toLocaleString()}
              </span>
              {latestCommit.isUnusual && (
                <div className="mt-2 text-sm text-red-600 flex items-center gap-2">
                  <Clock size={16} />
                  <span>Committed at an unusual time</span>
                </div>
              )}
              {latestCommit.isVulnerable && (
                <div className="mt-2 text-sm text-red-600 flex items-center gap-2">
                  <Shield size={16} />
                  <span>Potential security vulnerability detected</span>
                </div>
              )}
            </div>
          )}
          {alerts.length === 0 && (
            <div className="text-gray-500 text-sm">No active alerts at the moment.</div>
          )}
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="border-l-4 border-red-500 bg-red-50 p-3 rounded cursor-pointer hover:bg-red-100 transition-colors"
              onClick={() => setSelectedAlert(alert)}
            >
              <div className="flex items-center gap-2">
                {getSeverityIcon(alert.severity)}
                <h3 className="font-medium">{alert.title}</h3>
              </div>
              <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
              <span className="text-xs text-gray-500 mt-2 block">
                {alert.timestamp.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      <Modal 
        isOpen={selectedAlert !== null}
        onClose={() => setSelectedAlert(null)}
      >
        {selectedAlert && <AlertDetail alert={selectedAlert} />}
      </Modal>
    </>
  );
};