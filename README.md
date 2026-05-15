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

Сплошные стрелки — основной поток запроса пользователя (`клиент → Web → Gateway → доменные сервисы`) и интеграции с внешними системами. Пунктирные с подписями — синхронные REST-вызовы между доменными сервисами. Под каждым сервисом — его собственная БД (общих баз между сервисами нет).

```mermaid
flowchart TB
    classDef actor fill:#fef3c7,stroke:#a16207,color:#000
    classDef client fill:#dbeafe,stroke:#1d4ed8,color:#000
    classDef gateway fill:#fed7aa,stroke:#9a3412,color:#000
    classDef service fill:#dcfce7,stroke:#166534,color:#000
    classDef db fill:#e5e7eb,stroke:#374151,color:#000
    classDef ext fill:#fecaca,stroke:#991b1b,color:#000

    buyer(("Покупатель")):::actor
    seller(("Продавец")):::actor

    web["Web / Mobile App"]:::client
    gw["API Gateway"]:::gateway

    subgraph svc["Доменные сервисы"]
        direction TB
        subgraph services_row [" "]
            direction LR
            users["Users"]:::service
            catalog["Catalog"]:::service
            recs["Recommendations<br/><i>без БД</i>"]:::service
            orders["Orders"]:::service
            payments["Payments"]:::service
            notify["Notifications"]:::service
        end
        subgraph dbs_row [" "]
            direction LR
            users_db[("Users DB")]:::db
            catalog_db[("Catalog DB")]:::db
            orders_db[("Orders DB")]:::db
            payments_db[("Payments DB")]:::db
            notify_db[("Notify DB")]:::db
        end
        users --- users_db
        catalog --- catalog_db
        orders --- orders_db
        payments --- payments_db
        notify --- notify_db
    end

    psp["Payment Provider"]:::ext
    channels["Email / Push / SMS"]:::ext

    buyer -- HTTPS --> web
    seller -- HTTPS --> web
    web -- REST --> gw
    gw -- REST --> svc

    recs -. профиль .-> users
    recs -. товары .-> catalog
    orders -. остатки .-> catalog
    orders -. списание .-> payments
    orders -. статус .-> notify

    payments -- HTTPS --> psp
    notify -- HTTPS --> channels

    style services_row fill:transparent,stroke-width:0px
    style dbs_row fill:transparent,stroke-width:0px
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
