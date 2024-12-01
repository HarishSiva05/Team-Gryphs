import React, { useState, useRef, useEffect } from 'react';
import { Message } from './types';
import { ChatMessage } from './components/ChatMessage';
import { AlertPanel } from './components/AlertPanel';
import { RepositoryStatus } from './components/RepositoryStatus';
import KestraWorkflow  from './components/KestraWorkflow';
import { sendMessage } from './services/api';
import { mockAlerts, mockRepositories } from './data/mockData';
import { Send, Shield } from 'lucide-react';

interface Commit {
  repo: string;
  pusher: string;
  message: string;
  timestamp: string;
}

interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    content: "Hello! I'm your AI security assistant. How can I help you monitor your repository security today?",
    sender: 'bot',
    timestamp: new Date(),
    type: 'normal'
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [latestCommit, setLatestCommit] = useState<Commit | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:5000/events');
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'commit') {
        setLatestCommit(data);
        const commitMessage: Message = {
          id: Date.now().toString(),
          content: `New commit in ${data.repo} by ${data.pusher}: ${data.message}`,
          sender: 'bot',
          timestamp: new Date(data.timestamp),
          type: 'commit'
        };
        setMessages(prev => [...prev, commitMessage]);
      } else if (data.type === 'alert') {
        const newAlert: Alert = {
          id: Date.now().toString(),
          title: 'Unusual Commit Detected',
          description: data.message,
          severity: 'high',
          timestamp: new Date()
        };
        setAlerts(prev => [newAlert, ...prev]);
        const alertMessage: Message = {
          id: Date.now().toString(),
          content: data.message,
          sender: 'bot',
          timestamp: new Date(),
          type: 'alert'
        };
        setMessages(prev => [...prev, alertMessage]);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const botResponse = await sendMessage(input);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: botResponse,
        sender: 'bot',
        timestamp: new Date(),
        type: botResponse.startsWith('Error:') ? 'alert' : 'normal',
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error getting bot response:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please check your network connection and try again.",
        sender: 'bot',
        timestamp: new Date(),
        type: 'alert',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center mb-8">
          <Shield className="text-blue-600 w-8 h-8 mr-2" />
          <h1 className="text-2xl font-bold text-gray-800">
            Repository Security Assistant
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
              <div className="flex-1 overflow-y-auto p-4">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSubmit} className="p-4 border-t">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your security question..."
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:border-blue-500"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition-colors disabled:opacity-50"
                    disabled={isLoading}
                  >
                    <Send size={20} />
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div className="space-y-6">
            <AlertPanel alerts={alerts} latestCommit={latestCommit} />
            <RepositoryStatus repositories={mockRepositories} />
            <KestraWorkflow />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

