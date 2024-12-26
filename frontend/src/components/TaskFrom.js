// frontend/src/components/TaskForm.js

import React, { useState } from 'react';

const TaskForm = () => {
    const [expression, setExpression] = useState('');
    const [pointA, setPointA] = useState('');
    const [pointB, setPointB] = useState('');
    const [ttl, setTtl] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        const response = await fetch('http://localhost:5000/tasks', {  // Убедитесь, что URL правильный
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                expression,
                point_a: parseFloat(pointA),
                point_b: parseFloat(pointB),
                ttl: parseInt(ttl),
            }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(`Задача создана с ID: ${data.task_id}`);
        } else {
            alert('Ошибка при создании задачи');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Уравнение"
                value={expression}
                onChange={(e) => setExpression(e.target.value)}
                required
            />
            <input
                type="number"
                placeholder="Точка A"
                value={pointA}
                onChange={(e) => setPointA(e.target.value)}
                required
            />
            <input
                type="number"
                placeholder="Точка B"
                value={pointB}
                onChange={(e) => setPointB(e.target.value)}
                required
            />
            <input
                type="number"
                placeholder="TTL (мс)"
                value={ttl}
                onChange={(e) => setTtl(e.target.value)}
                required
            />
            <button type="submit">Отправить задачу</button>
        </form>
    );
};

export default TaskForm;
