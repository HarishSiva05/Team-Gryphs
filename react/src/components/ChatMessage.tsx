import React from 'react';
import { Message } from '../types';
import { AlertTriangle, Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isBot = message.sender === 'bot';
  
  return (
    <div className={`flex gap-3 ${isBot ? 'flex-row' : 'flex-row-reverse'} mb-4`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center
        ${isBot ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'}`}>
        {isBot ? <Bot size={20} /> : <User size={20} />}
      </div>
      <div className={`max-w-[80%] rounded-lg p-3 ${
        isBot 
          ? 'bg-white border border-gray-200' 
          : 'bg-blue-600 text-white'
      }`}>
        {message.type === 'alert' && (
          <div className="flex items-center gap-2 mb-2 text-red-500">
            <AlertTriangle size={16} />
            <span className="font-semibold">Security Alert</span>
          </div>
        )}
        <p className={`text-sm ${isBot ? 'text-gray-800' : 'text-white'}`}>
          {message.content}
        </p>
        <span className={`text-xs mt-1 block ${
          isBot ? 'text-gray-500' : 'text-blue-100'
        }`}>
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};