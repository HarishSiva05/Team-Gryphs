const responses = {
    greetings: [
      "Hello! I'm your security assistant. How can I help you today?",
      "Hi there! I'm here to help with your repository security. What would you like to know?",
    ],
    alerts: [
      "I've detected some security concerns that need attention. Would you like me to show you the details?",
      "There are active security alerts that require review. Shall I list them for you?",
    ],
    unknown: [
      "I'm not sure I understand. Could you rephrase that?",
      "I didn't quite catch that. Could you please clarify?",
    ],
  };
  
  export const generateResponse = (input: string): string => {
    const lowercaseInput = input.toLowerCase();
    
    if (lowercaseInput.includes('hello') || lowercaseInput.includes('hi')) {
      return responses.greetings[Math.floor(Math.random() * responses.greetings.length)];
    }
    
    if (lowercaseInput.includes('alert') || lowercaseInput.includes('warning')) {
      return responses.alerts[Math.floor(Math.random() * responses.alerts.length)];
    }
    
    return responses.unknown[Math.floor(Math.random() * responses.unknown.length)];
  }; 