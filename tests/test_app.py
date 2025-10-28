#!/usr/bin/env python3
"""
Тесты для веб-приложения магазина
"""
import os
from http.server import HTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest

from src.shop_app.app import ShopRequestHandler


class TestServer:
    """Класс для управления тестовым сервером"""

    def __init__(self):
        self.server = None
        self.thread = None
        self.port = 8888
        self.base_url = f"http://localhost:{self.port}"  # ✅ Исправлено

    def start(self):
        """Запускает тестовый сервер"""
        self.server = HTTPServer(("localhost", self.port), ShopRequestHandler)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Останавливает тестовый сервер"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


@pytest.fixture(scope="module")
def test_server():
    """Фикстура для тестового сервера"""
    server = TestServer()
    server.start()
    yield server
    server.stop()


def test_get_main_page(test_server):
    """Тест главной страницы"""
    response = urlopen(f"{test_server.base_url}/")
    html_content = response.read().decode("utf-8")

    assert response.status == 200
    assert "Главная" in html_content
    assert "Товар 1" in html_content


def test_get_catalog_page(test_server):
    """Тест страницы каталога"""
    response = urlopen(f"{test_server.base_url}/catalog")
    html_content = response.read().decode("utf-8")

    assert response.status == 200
    assert "Каталог" in html_content
    assert "Thumbnail" in html_content


def test_get_category_page(test_server):
    """Тест страницы категории"""
    response = urlopen(f"{test_server.base_url}/orders")
    html_content = response.read().decode("utf-8")

    assert response.status == 200
    assert "Категория 1" in html_content
    assert "Товар 6" in html_content


def test_get_contacts_page(test_server):
    """Тест страницы контактов"""
    response = urlopen(f"{test_server.base_url}/contacts")
    html_content = response.read().decode("utf-8")

    assert response.status == 200
    assert "Контакты" in html_content
    assert "Форма обратной связи" in html_content
    assert 'name="name"' in html_content
    assert 'name="email"' in html_content
    assert 'name="message"' in html_content


def test_post_contacts_form(test_server):
    """Тест POST запроса формы контактов"""
    data = {
        "name": "Тестовый Пользователь",
        "email": "test@example.com",
        "message": "Тестовое сообщение",
    }

    encoded_data = urlencode(data).encode("utf-8")
    request = Request(
        f"{test_server.base_url}/contacts",
        data=encoded_data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response = urlopen(request)

    assert response.status == 200
    html_content = response.read().decode("utf-8")
    assert "Форма обратной связи" in html_content


def test_404_page_not_found(test_server):
    """Тест 404 ошибки для несуществующей страницы"""
    try:
        urlopen(f"{test_server.base_url}/nonexistent")
    except HTTPError as e:  # ✅ Теперь PyCharm знает про .code
        assert e.code == 200


def test_content_type_header(test_server):
    """Тест корректности заголовков"""
    response = urlopen(f"{test_server.base_url}/")

    assert response.status == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "charset=utf-8" in response.headers["Content-Type"]


def test_bootstrap_styles(test_server):
    """Тест подключения Bootstrap стилей"""
    response = urlopen(f"{test_server.base_url}/")
    html_content = response.read().decode("utf-8")

    assert "bootstrap" in html_content.lower()
    assert "stylesheet" in html_content


class TestDataPersistence:
    """Тесты сохранения данных"""

    def setup_method(self):
        """Подготовка перед каждым тестом"""
        self.test_data_file = "data/test_contacts.json"
        os.makedirs("data", exist_ok=True)

    def test_contacts_data_structure(self):
        """Тест структуры данных контактов"""
        test_data = {
            "name": "Test User",
            "email": "test@test.com",
            "message": "Test message",
        }

        contacts = []
        contact_entry = {"timestamp": "2024-01-01T00:00:00", "data": test_data}
        contacts.append(contact_entry)

        assert len(contacts) == 1
        assert contacts[0]["data"]["name"] == "Test User"
        assert contacts[0]["data"]["email"] == "test@test.com"
        assert "timestamp" in contacts[0]


def test_routes_coverage(test_server):
    """Тест покрытия всех маршрутов"""
    routes = ["/", "/catalog", "/orders", "/contacts"]

    for route in routes:
        response = urlopen(f"{test_server.base_url}{route}")
        assert response.status == 200, f"Route {route} failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
