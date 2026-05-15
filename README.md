# ДЗ-1. Маркетплейс: C4 + сервис в Docker

Архитектура цифрового маркетплейса на уровне C4 Container и один работающий сервис (`api-gateway`), поднимаемый в Docker. По условию задания бизнес-логика не реализуется.

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

Исходник: [`diagrams/container.puml`](diagrams/container.puml). Версия в Mermaid для быстрого просмотра:

```mermaid
flowchart TB
    buyer(("Покупатель"))
    seller(("Продавец"))

    subgraph mp["Marketplace"]
        web["Web / Mobile App<br/><i>React / iOS / Android</i>"]
        gw["API Gateway<br/><i>FastAPI</i>"]

        subgraph services["Доменные сервисы"]
            users["Users"]
            catalog["Catalog"]
            recs["Recommendations"]
            orders["Orders"]
            payments["Payments"]
            notify["Notifications"]
        end

        users_db[("Users DB")]
        catalog_db[("Catalog DB")]
        recs_db[("Recs DB")]
        orders_db[("Orders DB")]
        payments_db[("Payments DB")]
        notify_db[("Notify DB")]
    end

    psp["Payment Provider"]
    channels["Email / Push / SMS"]

    buyer -- HTTPS --> web
    seller -- HTTPS --> web
    web -- REST --> gw

    gw --> users
    gw --> catalog
    gw --> recs
    gw --> orders
    gw --> payments
    gw --> notify

    recs --> catalog
    recs --> users
    orders --> catalog
    orders --> payments
    orders --> notify

    users --> users_db
    catalog --> catalog_db
    recs --> recs_db
    orders --> orders_db
    payments --> payments_db
    notify --> notify_db

    payments -- HTTPS --> psp
    notify -- HTTPS --> channels
```

### Контейнеры и зоны ответственности

| Контейнер | Технология | Ответственность | Свои данные |
|---|---|---|---|
| Web / Mobile App | React / iOS / Android | Клиент | — |
| API Gateway | FastAPI | Единая точка входа, маршрутизация | — |
| Users | — | Пользователи, авторизация, профиль | Users DB |
| Catalog | — | Товары, категории, остатки | Catalog DB |
| Recommendations | — | Персональная лента | Recs DB |
| Orders | — | Корзина, заказы, статусы | Orders DB |
| Payments | — | Платежи и выплаты | Payments DB |
| Notifications | — | Уведомления о статусах | Notify DB |

Каждый доменный сервис владеет своей БД, общих баз между сервисами нет; обращение к чужим данным — только через REST API соответствующего сервиса. Это даёт независимое масштабирование, изоляцию платежей и персональных данных, и прямое соответствие пунктам ТЗ (лента → Recommendations, каталог → Catalog, пользователи → Users, заказы → Orders, платежи → Payments, уведомления → Notifications).

В Docker в рамках ДЗ поднимается один сервис — `api-gateway`, поскольку именно он является точкой входа в систему и удобен для демонстрации `/health`-endpoint'а.

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
