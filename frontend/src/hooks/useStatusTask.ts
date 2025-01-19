import { useState, useEffect } from 'react';

interface TaskStatus {
  status: "Finished" | "Failed" | "Unknown";
}

function useTaskStatus(taskId: string) {
  const [status, setStatus] = useState<string>('In Progress');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(`/api/task_status_stream/${taskId}`);

    eventSource.onmessage = function (event) {
      const data: TaskStatus = JSON.parse(event.data);
      setStatus(data.status);

      if (data.status === 'Finished' || data.status === 'Failed') {
        eventSource.close(); 
      }
    };

    eventSource.onerror = (error: any) => {
      setError(`Wystąpił błąd przy połączeniu z serwerem. ${error}`);
      eventSource.close();
    };

   
    return () => {
      eventSource.close();
    };
  }, [taskId]);

  return { status, error };
}

export default useTaskStatus;