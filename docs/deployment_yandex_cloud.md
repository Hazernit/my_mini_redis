# Размещение проекта в Yandex Cloud

## Общая схема

Проект состоит из двух частей:

- статический сайт из папки `site`;
- backend: TCP Mini Redis Server и HTTP API.

Для MVP удобно разместить сайт в Yandex Object Storage, а backend запустить на виртуальной машине Yandex Compute Cloud через Docker Compose.

```text
Браузер / телефон
        |
        | открывает статический сайт
        v
Yandex Object Storage
        |
        | fetch к API_URL
        v
VM в Yandex Compute Cloud: порт 8080
        |
        | docker network
        v
mini-redis-api -> mini-redis-server
```

## Локальный запуск без Docker

Локальный запуск остается прежним.

В первом терминале:

```bash
python src/server.py
```

Во втором терминале:

```bash
python src/api.py
```

В третьем терминале:

```bash
python3 -m http.server 8000
```

После запуска сайт доступен по адресу:

```text
http://127.0.0.1:8000/site/demo.html
```

HTTP API по умолчанию слушает `0.0.0.0:8080`. Для локальной проверки это не мешает: браузер по-прежнему обращается к `http://127.0.0.1:8080`.

## Локальный запуск через Docker Compose

Из корня проекта:

```bash
docker compose up -d --build
```

Проверка API:

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/command \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"PING\"}"
```

Остановка:

```bash
docker compose down
```

В `docker-compose.yml` запускаются два сервиса:

- `mini-redis-server` — TCP-сервер на порту `6379`;
- `mini-redis-api` — HTTP API на порту `8080`.

API обращается к серверу по переменным окружения:

```text
MINI_REDIS_HOST=mini-redis-server
MINI_REDIS_PORT=6379
```

## Запуск backend на VM

1. Создайте виртуальную машину в Yandex Compute Cloud.
2. Назначьте VM публичный IP-адрес.
3. Подключитесь к VM по SSH.
4. Установите Git и Docker.

Пример для Ubuntu:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

Клонируйте репозиторий:

```bash
git clone https://github.com/Hazernit/my_mini_redis.git
cd my_mini_redis
```

Запустите backend:

```bash
docker compose up -d --build
```

Проверьте API на VM:

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/command \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"PING\"}"
```

С внешнего компьютера API должен открываться по адресу:

```text
http://PUBLIC_VM_IP:8080/health
```

## Как открыть порт 8080

В группе безопасности VM нужно добавить входящее правило:

- направление: входящий трафик;
- протокол: TCP;
- порт: `8080`;
- источник: `0.0.0.0/0` для учебного MVP.

Для SSH также должен быть открыт порт `22`.

Порт `6379` наружу открывать не нужно: HTTP API обращается к `mini-redis-server` внутри Docker-сети.

## Как заменить API_URL

Перед загрузкой сайта в Object Storage откройте файл `site/script.js`.

Для локального запуска:

```js
const API_URL = "http://127.0.0.1:8080";
```

Для Yandex Cloud замените адрес на публичный IP виртуальной машины:

```js
const API_URL = "http://PUBLIC_VM_IP:8080";
```

После замены сохраните файл и загрузите папку `site` в Object Storage.

## Загрузка папки site в Object Storage

Через консоль Yandex Cloud:

1. Откройте Object Storage.
2. Создайте публичный бакет.
3. Включите хостинг статического сайта.
4. Укажите `index.html` как главную страницу.
5. Загрузите все файлы из папки `site`:
   - `index.html`;
   - `about.html`;
   - `projects.html`;
   - `research.html`;
   - `journal.html`;
   - `resources.html`;
   - `demo.html`;
   - `script.js`;
   - `styles.css`.
6. Проверьте, что сайт открывается по адресу бакета.

Важно: если сайт открыт по HTTPS, а API доступен только по HTTP, браузер может заблокировать запросы как mixed content. Для MVP можно использовать HTTP-адрес сайта. Для полноценного публичного размещения лучше настроить HTTPS для API через reverse proxy.

## Как открыть сайт с телефона

1. Убедитесь, что VM запущена.
2. Убедитесь, что Docker Compose сервисы работают:

```bash
docker compose ps
```

3. Проверьте с компьютера:

```text
http://PUBLIC_VM_IP:8080/health
```

4. Откройте на телефоне публичный адрес сайта из Object Storage.
5. Перейдите на страницу `demo.html`.
6. Выполните `PING`, затем `SET`, `GET`, `KEYS` или другую команду.

Если телефон не получает ответ от API, проверьте:

- открыт ли порт `8080` в Security Group;
- правильно ли указан `API_URL` в `site/script.js`;
- запущены ли контейнеры `mini-redis-server` и `mini-redis-api`;
- не блокирует ли браузер запрос с HTTPS-сайта на HTTP API.

## Полезные ссылки

- Yandex Object Storage: https://yandex.cloud/ru/docs/storage/
- Хостинг статических сайтов: https://yandex.cloud/ru/docs/storage/concepts/hosting
- Настройка хостинга Object Storage: https://yandex.cloud/ru/docs/storage/operations/hosting/setup
- Группы безопасности VPC: https://yandex.cloud/en/docs/vpc/concepts/security-groups
- Добавление правила в группу безопасности: https://yandex.cloud/ru/docs/vpc/operations/security-group-add-rule

## Ограничения MVP

- Данные хранятся в памяти и исчезают после перезапуска контейнера `mini-redis-server`.
- HTTP API не содержит авторизации.
- Порт `8080` открыт публично для демонстрации.
- Для продакшена нужны HTTPS, reverse proxy, домен и ограничение доступа.
