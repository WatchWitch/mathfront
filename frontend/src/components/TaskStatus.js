// frontend/src/components/TaskStatus.js

import React, { useState } from 'react';

const TaskStatus = () => {
    const [taskId, setTaskId] = useState('');
    const [status, setStatus] = useState('');

    const handleCheckStatus = async () => {
        const response = await fetch(`/tasks/${taskId}`);
        if (response.ok) {
            const data = await response.json();
            setStatus(`Статус задачи: ${data.status}`);
        } else {
            setStatus('Задача не найдена');
        }
    };

    return (
        <div>
            <input
                type="text"
                placeholder="ID задачи"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
                required
            />
            <button onClick={handleCheckStatus}>Проверить статус</button>
            <p>{status}</p>
        </div>
    );
};

export default TaskStatus;