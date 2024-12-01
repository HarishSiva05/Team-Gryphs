import { Alert, Repository } from '../types';

export const mockAlerts: Alert[] = [
  {
    id: '1',
    title: 'Suspicious Commit Pattern Detected',
    description: 'Multiple large commits outside normal working hours',
    severity: 'medium',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: '2',
    title: 'Sensitive Data Exposure',
    description: 'Potential API key committed in recent changes',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
  },
  {
    id: '3',
    title: 'Dependency Version Mismatch',
    description: 'Critical security updates pending for 3 packages',
    severity: 'medium',
    timestamp: new Date(Date.now() - 1000 * 60 * 120),
  },
];

export const mockRepositories: Repository[] = [
  {
    name: 'frontend-app',
    status: 'secure',
    lastScan: new Date(Date.now() - 1000 * 60 * 15),
  },
  {
    name: 'api-service',
    status: 'warning',
    lastScan: new Date(Date.now() - 1000 * 60 * 25),
  },
  {
    name: 'auth-module',
    status: 'critical',
    lastScan: new Date(Date.now() - 1000 * 60 * 35),
  },
];