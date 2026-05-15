# ДЗ-1. Маркетплейс: C4 + сервис в Docker

## Структура

```
hw-1/
├── README.md
├── docker-compose.yml
├── diagrams/
│   └── container.puml       # C4 Container диаграмма (PlantUML)
└── api-gateway/             # сервис, поднимаемый в Docker
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        └── main.py
```

## C4 Container

Исходник: [`diagrams/container.puml`](diagrams/container.puml).

Стандартная нотация C4 Container: actors-стикмены, синие прямоугольники — контейнеры, синие цилиндры — БД, серые блоки — внешние системы, пунктирная рамка — граница системы. Раскладка широкая (LR), у Recommendations собственной БД нет — он не имеет своих сущностей и собирает ленту из Users и Catalog.

```mermaid
C4Container
    title C4 Container - Marketplace

    Person(buyer, "Покупатель")
    Person(seller, "Продавец")

    System_Boundary(mp, "Marketplace") {
      Container(web, "Web / Mobile App", "client", "клиентское приложение")
      Container(gw, "API Gateway", "FastAPI", "единая точка входа, маршрутизация")

      Container(users, "Users", "service", "пользователи, авторизация, профиль")
      Container(catalog, "Catalog", "service", "товары, категории, остатки")
      Container(recs, "Recommendations", "service (stateless)", "персональная лента")
      Container(orders, "Orders", "service", "корзина, заказы, статусы")
      Container(payments, "Payments", "service", "платежи и выплаты")
      Container(notify, "Notifications", "service", "уведомления о статусах")

      ContainerDb(users_db, "Users DB", "PostgreSQL")
      ContainerDb(catalog_db, "Catalog DB", "PostgreSQL")
      ContainerDb(orders_db, "Orders DB", "PostgreSQL")
      ContainerDb(payments_db, "Payments DB", "PostgreSQL")
      ContainerDb(notify_db, "Notify DB", "PostgreSQL")
    }

    System_Ext(psp, "Payment Provider", "внешняя платёжная система")
    System_Ext(channels, "Email / Push / SMS", "внешние провайдеры уведомлений")

    Rel(buyer, web, "HTTPS")
    Rel(seller, web, "HTTPS")
    Rel(web, gw, "REST", "HTTPS")

    Rel(gw, users, "REST")
    Rel(gw, catalog, "REST")
    Rel(gw, recs, "REST")
    Rel(gw, orders, "REST")
    Rel(gw, payments, "REST")
    Rel(gw, notify, "REST")

    Rel(recs, users, "профиль", "REST")
    Rel(recs, catalog, "товары", "REST")
    Rel(orders, catalog, "остатки", "REST")
    Rel(orders, payments, "списание", "REST")
    Rel(orders, notify, "статус", "REST")

    Rel(users, users_db, "SQL")
    Rel(catalog, catalog_db, "SQL")
    Rel(orders, orders_db, "SQL")
    Rel(payments, payments_db, "SQL")
    Rel(notify, notify_db, "SQL")

    Rel(payments, psp, "платежи", "HTTPS")
    Rel(notify, channels, "отправка", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

Каждый доменный сервис владеет своей БД, общих баз между сервисами нет — доступ к чужим данным только через REST API соответствующего сервиса. Это даёт независимое масштабирование, изоляцию платежей и персональных данных и прямое соответствие пунктам ТЗ (лента → Recommendations, каталог → Catalog, пользователи → Users, заказы → Orders, платежи → Payments, уведомления → Notifications).

Recommendations — единственный сервис без собственной БД: у него нет своих доменных сущностей, он на каждый запрос собирает ленту, дёргая Users (профиль) и Catalog (товары). Логи взаимодействий и кеши предсказаний (Redis / фича-стор) можно ввести эволюционно позже, когда понадобится более тяжёлая персонализация.

В Docker в рамках ДЗ поднимается один сервис — `api-gateway`, как точка входа в систему.

## Запуск

Требования: Docker и Docker Compose.

```bash
cd hw-1
docker compose up --build -d
```

Проверка `/health`:

```bash
curl -i http://localhost:8080/health
```

Ожидаемый ответ:

```
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

Остановить:

```bash
docker compose down
```
