#!/usr/bin/env python3
"""
Web application for online shop
"""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class ShopRequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов для интернет-магазина"""

    def __init__(self, *args, **kwargs):
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        super().__init__(*args, **kwargs)

    def _send_html_response(self, file_name, status_code=200):  # ✅ lowercase
        """Отправляет HTML-ответ"""
        try:
            file_path = os.path.join(self.templates_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            self.send_response(status_code)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        except FileNotFoundError:
            self._send_error_response(404, f"Страница {file_name} не найдена")

    def _send_error_response(self, status_code, message):  # ✅ lowercase
        """Отправляет ошибку"""
        self.send_response(status_code)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        error_html = f"""    
        <!DOCTYPE html>
        <html>
        <head>
            <title> Ошибка {status_code} </title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="alert alert-danger">
                    <h1> Ошибка {status_code} </h1>
                    <p> {message} </p>
                    <a href="/" class="btn btn-primary">Вернуться на главную</a>
                </div>
            </div>
        </body>
        </html>
                  """
        self.wfile.write(error_html.encode("utf-8"))

    def _log_request(self):
        """Логирует информацию о запросе"""
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.command} {self.path}"
        )

    def do_GET(self):
        """Обрабатывает GET-запросы"""
        self._log_request()

        # Парсим URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Маршрутизация - ПО ТВОЕМУ!
        routes = {
            "/": "index.html",  # Главная
            "/catalog": "catalog.html",  # Каталог (открывается по "Категории")
            "/orders": "category.html",  # Категория 1 (открывается по "Заказы")
            "/contacts": "contacts.html",  # Контакты
        }

        html_file = routes.get(path, "contacts.html")
        self._send_html_response(html_file)

    def do_POST(self):  # noqa: N802
        """Обрабатывает POST-запросы"""
        self._log_request()

        if self.path == "/contacts":
            # Читаем данные формы
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            # Парсим данные
            parsed_data = parse_qs(post_data.decode("utf-8"))

            # Логируем в консоль (дополнительное задание)
            self._log_post_data(parsed_data)

            # Сохраняем в файл (бонус)
            self._save_contact_data(parsed_data)

            # Возвращаем ответ
            self._send_success_response()
        else:
            self._send_error_response(405, "Метод не поддерживается")

    @staticmethod  # ✅ Добавляем staticmethod
    def _log_post_data(data):
        """Логирует POST-данные в консоль"""
        print("=" * 60)
        print("POST ДАННЫЕ ОТ ФОРМЫ КОНТАКТОВ:")
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        for key, value in data.items():
            print(f"  {key}: {value[0]}")
        print("=" * 60)

    @staticmethod  # ✅ Добавляем staticmethod
    def _save_contact_data(data):
        """Сохраняет данные формы в файл (бонусная функция)"""
        try:
            contacts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
            os.makedirs(contacts_dir, exist_ok=True)

            contact_file = os.path.join(contacts_dir, "contacts.json")

            # Читаем существующие данные
            contacts = []
            if os.path.exists(contact_file):
                with open(contact_file, "r", encoding="utf-8") as f:
                    contacts = json.load(f)

            # Добавляем новые данные
            contact_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": {key: value[0] for key, value in data.items()},
            }
            contacts.append(contact_entry)

            # Сохраняем
            with open(contact_file, "w", encoding="utf-8") as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")

    def _send_success_response(self):  # ✅ lowercase
        """Отправляет успешный ответ после POST"""
        try:
            file_path = os.path.join(self.templates_dir, "contacts.html")
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            # Добавляем сообщение об успехе
            success_message = """
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <strong>Успех!</strong> Ваше сообщение отправлено и сохранено!
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            """

            modified_html = html_content.replace(
                '<h5 class="card-title">Форма обратной связи</h5>',
                f'<h5 class="card-title">Форма обратной связи</h5>{success_message}',
            )

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(modified_html.encode("utf-8"))

        except FileNotFoundError:
            self._send_error_response(500, "Ошибка сервера")


def run_server(host="localhost", port=8000):
    """Запускает веб-сервер"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, ShopRequestHandler)

    print("=" * 50)
    print("🚀 ВЕБ-ПРИЛОЖЕНИЕ ЗАПУЩЕНО!")
    print("=" * 50)
    print(f"📍 Сервер запущен на: http: //{host}: {port}")
    print("📁 Доступные страницы:")
    print(f"   • http: //{host}: {port}/ - Главная")
    print(f"   • http: //{host}: {port}/catalog - Каталог")
    print(f"   • http: //{host}: {port}/category - Категория")
    print(f"   • http: //{host}: {port}/contacts - Контакты")
    print(f"   • http: //{host}: {port}/orders - Заказы")
    print("=" * 50)
    print("ℹ️  POST-данные сохраняются в data/contacts.json")
    print("🛑 Для остановки сервера нажмите Ctrl+C")
    print("=" * 50)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")


if __name__ == "__main__":
    run_server()
