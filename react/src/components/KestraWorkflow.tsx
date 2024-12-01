import React, { useState } from 'react';
import axios from 'axios';
import { triggerWorkflow, getWorkflowStatus } from '../services/kestraServices';

const KestraWorkflow: React.FC = () => {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<string>('Rick Astley');
  const [output, setOutput] = useState<string | null>(null);

  const handleTriggerWorkflow = async () => {
    try {
      setError(null);
      setOutput(null);
      const result = await triggerWorkflow('tutorial', 'hello-world', { user });
      setExecutionId(result.id);
    } catch (error) {
      console.error('Failed to trigger workflow:', error);
      let errorMessage = 'Failed to trigger workflow. ';
      if (axios.isAxiosError(error)) {
        errorMessage += `Status: ${error.response?.status}. `;
        errorMessage += `Message: ${error.response?.data?.message || error.message}`;
      } else {
        errorMessage += String(error);
      }
      setError(errorMessage);
    }
  };

  const handleCheckStatus = async () => {
    if (!executionId) return;
    try {
      setError(null);
      const result = await getWorkflowStatus(executionId);
      setStatus(result.state);
      if (result.state === 'SUCCESS') {
        const taskOutputs = result.taskRunList.find((task: { taskId: string; }) => task.taskId === 'hello_world')?.outputs;
        if (taskOutputs && taskOutputs.message) {
          setOutput(taskOutputs.message);
        }
      }
    } catch (error) {
      console.error('Failed to check workflow status:', error);
      let errorMessage = 'Failed to check workflow status. ';
      if (axios.isAxiosError(error)) {
        errorMessage += `Status: ${error.response?.status}. `;
        errorMessage += `Message: ${error.response?.data?.message || error.message}`;
      } else {
        errorMessage += String(error);
      }
      setError(errorMessage);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold mb-4">Kestra Workflow: Hello World</h2>
      <div className="mb-4">
        <label htmlFor="user" className="block text-sm font-medium text-gray-700">User Name:</label>
        <input
          type="text"
          id="user"
          value={user}
          onChange={(e) => setUser(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        />
      </div>
      <button 
        onClick={handleTriggerWorkflow}
        className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition-colors mb-2 w-full"
      >
        Trigger Workflow
      </button>
      {executionId && (
        <>
          <p className="text-sm text-gray-600 mb-2">Execution ID: {executionId}</p>
          <button 
            onClick={handleCheckStatus}
            className="bg-green-600 text-white rounded-lg px-4 py-2 hover:bg-green-700 transition-colors mb-2 w-full"
          >
            Check Status
          </button>
        </>
      )}
      {status && <p className="text-sm font-semibold mb-2">Workflow Status: {status}</p>}
      {output && (
        <div className="bg-gray-100 p-2 rounded-md mb-2">
          <h3 className="text-sm font-semibold">Workflow Output:</h3>
          <p className="text-sm">{output}</p>
        </div>
      )}
      {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
    </div>
  );
};

export default KestraWorkflow;

