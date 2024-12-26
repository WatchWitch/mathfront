# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from worker import process_task 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks_data.db'  # Замените на вашу БД
db = SQLAlchemy(app)
CORS(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.TEXT, nullable=False)
    point_a = db.Column(db.REAL, nullable=False)
    point_b = db.Column(db.REAL, nullable=False)
    ttl = db.Column(db.Integer, nullable=False)
    status = db.Column(db.TEXT, default='В очереди')  # Статус задачи
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime, nullable=True)  # Дата и время завершения задачи
    newton_result = db.Column(db.REAL, nullable=True)  # Результат метода Ньютона
    segment_result = db.Column(db.REAL, nullable=True)  # Результат метода бисекции

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    expression = data['expression']
    point_a = data['point_a']
    point_b = data['point_b']
    ttl = data['ttl']

    task = Task(expression=expression, point_a=point_a, point_b=point_b, ttl=ttl)
    db.session.add(task)
    db.session.commit()

    # Запускаем выполнение задачи в фоновом режиме
    process_task(task.id)

    return jsonify({'task_id': task.id}), 201

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': task.id,
        'status': task.status,
        'expression': task.expression,
        'newton_result': task.newton_result,
        'segment_result': task.segment_result,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'ttl': task.ttl
    } for task in tasks])

if __name__ == '__main__':
    with app.app_context():  # Создаем контекст приложения
        db.create_all()  # Создание таблиц
    app.run(debug=True)  # Запуск приложения
