// types.ts
export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'normal' | 'alert' | 'commit';
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: Date;
}

export interface Commit {
  repo: string;
  pusher: string;
  message: string;
  timestamp: string;
  isUnusual: boolean;
  isVulnerable?: boolean;
  
}

export interface Repository {
  name: string;
  status: 'secure' | 'warning' | 'critical';
  lastScan: Date;
}