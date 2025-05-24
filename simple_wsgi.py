#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое WSGI приложение для демонстрации работы с параметрами
Запускается на localhost:8081 с помощью gunicorn
"""

import urllib.parse
from io import StringIO
import sys


def application(environ, start_response):
    """
    Основная WSGI функция приложения
    """
    # Получаем метод запроса
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Получаем GET параметры
    query_string = environ.get('QUERY_STRING', '')
    get_params = urllib.parse.parse_qs(query_string)
    
    # Получаем POST параметры
    post_params = {}
    if method == 'POST':
        try:
            # Получаем размер тела запроса
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            content_length = 0
        
        if content_length > 0:
            # Читаем тело запроса
            post_data = environ['wsgi.input'].read(content_length)
            if isinstance(post_data, bytes):
                post_data = post_data.decode('utf-8')
            post_params = urllib.parse.parse_qs(post_data)
    
    # Формируем HTML ответ
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WSGI Тестовое приложение</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            .section {{
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }}
            .method {{
                font-weight: bold;
                color: #007bff;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                padding: 5px 0;
                border-bottom: 1px solid #eee;
            }}
            .key {{
                font-weight: bold;
                color: #333;
            }}
            .value {{
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 WSGI Тестовое приложение</h1>
            
            <div class="section">
                <h2>Метод запроса: <span class="method">{method}</span></h2>
            </div>
            
            <div class="section">
                <h2>GET параметры:</h2>
                {format_params(get_params)}
            </div>
            
            <div class="section">
                <h2>POST параметры:</h2>
                {format_params(post_params)}
            </div>
            
            <div class="section">
                <h2>Тестовая форма:</h2>
                <form method="post" action="">
                    <p>
                        <label for="test_input">Тестовое поле:</label><br>
                        <input type="text" id="test_input" name="test_input" placeholder="Введите что-нибудь">
                    </p>
                    <p>
                        <label for="another_field">Ещё одно поле:</label><br>
                        <input type="text" id="another_field" name="another_field" placeholder="И сюда тоже">
                    </p>
                    <p>
                        <input type="submit" value="Отправить POST запрос">
                    </p>
                </form>
                
                <p><a href="?param1=test&param2=value&param3=123">Тестовая ссылка с GET параметрами</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Устанавливаем заголовки ответа
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html_content.encode('utf-8'))))
    ]
    
    start_response(status, response_headers)
    
    # Возвращаем содержимое как байты
    return [html_content.encode('utf-8')]


def format_params(params_dict):
    """
    Форматирует словарь параметров в HTML список
    """
    if not params_dict:
        return "<p><em>Параметры отсутствуют</em></p>"
    
    html = "<ul>"
    for key, values in params_dict.items():
        for value in values:
            html += f'<li><span class="key">{key}:</span> <span class="value">{value}</span></li>'
    html += "</ul>"
    return html


if __name__ == "__main__":
    # Для локального тестирования
    from wsgiref.simple_server import make_server
    
    print("Запуск тестового WSGI сервера на http://localhost:8081")
    print("Для остановки нажмите Ctrl+C")
    
    server = make_server('localhost', 8081, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен") 