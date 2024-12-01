import axios from 'axios';

const KESTRA_URL = 'http://localhost:8080';

export const triggerWorkflow = async (namespace: string, flowId: string, inputs?: Record<string, any>) => {
  try {
    console.log(`Triggering workflow: namespace=${namespace}, flowId=${flowId}, inputs=`, inputs);
    const response = await axios.post(`${KESTRA_URL}/api/v1/executions`, {
      namespace,
      flowId,
      inputs
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log('Workflow triggered successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error triggering Kestra workflow:', error);
    if (axios.isAxiosError(error)) {
      console.error('Response data:', error.response?.data);
      console.error('Response status:', error.response?.status);
      console.error('Response headers:', error.response?.headers);
    }
    throw error;
  }
};

export const getWorkflowStatus = async (executionId: string) => {
  try {
    const response = await axios.get(`${KESTRA_URL}/api/v1/executions/${executionId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching workflow status:', error);
    throw error;
  }
};

