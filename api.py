from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
import jwt
from worker import process_task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks_data.db'  # Заменить на БД
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для JWT
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

# Статичный аккаунт для авторизации
USER_CREDENTIALS = {
    'username': 'admin',
    'password': 'password123'  # Пароль для входа
}

# Генерация JWT токена
def generate_token():
    payload = {
        'username': USER_CREDENTIALS['username'],
        'exp': datetime.utcnow() + timedelta(hours=1)  # Токен действителен 1 час
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Проверка JWT токена
def verify_token(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None  # Неверный токен

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
        token = generate_token()
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Неверные учетные данные'}), 401

@app.route('/api/tasks', methods=['POST'])
def create_task():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Отсутствует токен'}), 403

    token = token.split(" ")[1]  # Извлекаем токен из заголовка "Bearer <token>"

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Токен истек'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Неверный токен'}), 401

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
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Отсутствует токен'}), 403

    token = token.split(" ")[1]  # Извлекаем токен из заголовка "Bearer <token>"

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Токен истек'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Неверный токен'}), 401

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