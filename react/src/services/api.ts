import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000';  // Make sure this matches your backend URL

export const sendMessage = async (message: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, { message });
    return response.data.response;
  } catch (error) {
    console.error('Error sending message:', error);
    if (axios.isAxiosError(error) && error.response) {
      return `Error: ${error.response.data.response || 'Unknown server error'}`;
    } else {
      return 'Error: Unable to connect to the server. Please try again later.';
    }
  }
};