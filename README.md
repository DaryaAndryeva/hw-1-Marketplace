# ДЗ-1. Маркетплейс: C4 + сервис в Docker

## C4 Container

```mermaid
flowchart LR
    classDef actor fill:#08427B,stroke:#052E5B,color:#fff
    classDef container fill:#438DD5,stroke:#2C6FAB,color:#fff
    classDef db fill:#438DD5,stroke:#2C6FAB,color:#fff
    classDef ext fill:#999999,stroke:#6B6B6B,color:#fff

    buyer(("Покупатель")):::actor
    seller(("Продавец")):::actor

    web["Web / Mobile App"]:::container
    gw["API Gateway"]:::container

    subgraph svc["Доменные сервисы"]
        direction LR
        subgraph p_users [" "]
            users["Users"]:::container
            users_db[("Users DB")]:::db
            users --- users_db
        end
        subgraph p_catalog [" "]
            catalog["Catalog"]:::container
            catalog_db[("Catalog DB")]:::db
            catalog --- catalog_db
        end
        subgraph p_recs [" "]
            recs["Recommendations<br/><i>stateless</i>"]:::container
        end
        subgraph p_orders [" "]
            orders["Orders"]:::container
            orders_db[("Orders DB")]:::db
            orders --- orders_db
        end
        subgraph p_payments [" "]
            payments["Payments"]:::container
            payments_db[("Payments DB")]:::db
            payments --- payments_db
        end
        subgraph p_notify [" "]
            notify["Notifications"]:::container
            notify_db[("Notify DB")]:::db
            notify --- notify_db
        end
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

    style p_users fill:transparent,stroke-width:0px
    style p_catalog fill:transparent,stroke-width:0px
    style p_recs fill:transparent,stroke-width:0px
    style p_orders fill:transparent,stroke-width:0px
    style p_payments fill:transparent,stroke-width:0px
    style p_notify fill:transparent,stroke-width:0px
```

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
