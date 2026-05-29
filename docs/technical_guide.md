# Техническое руководство

## 1. Подготовка проекта

Проект написан на Python и не требует внешних зависимостей. Для запуска достаточно установленного Python 3.

Рекомендуемая структура проекта:

```text
my_mini_redis/
├── src/
├── site/
├── docs/
├── reports/
└── task/
```

## 2. Реализация TCP-сервера

Файл `src/server.py` запускает TCP-сервер на адресе `127.0.0.1` и порту `6379`.

Основные шаги работы сервера:

1. Создать TCP-сокет.
2. Привязать сокет к адресу и порту.
3. Ожидать подключения клиентов.
4. Читать команды построчно.
5. Выполнять операции с хранилищем.
6. Возвращать ответ клиенту.

Команды обрабатываются в функции `execute_command`. Данные хранятся в словаре `STORE`.
Журнал выполненных команд хранится в списке `COMMAND_LOG`.

Поддерживаемые команды:

- `SET key value`;
- `GET key`;
- `DELETE key`;
- `EXISTS key`;
- `PING`;
- `KEYS`;
- `FLUSH`;
- `UPDATE key value`;
- `LOG`.

## 3. Реализация CLI-клиента

Файл `src/client.py` позволяет отправлять команды серверу из терминала.

Пример:

```bash
python src/client.py SET user Alice
python src/client.py GET user
python src/client.py PING
python src/client.py KEYS
python src/client.py UPDATE user Bob
python src/client.py LOG
```

Если запустить клиент без команды, он перейдет в интерактивный режим.

## 4. Реализация HTTP API

Файл `src/api.py` нужен для связи браузера с TCP-сервером. Браузер не может напрямую работать с произвольным TCP-сокетом, поэтому используется HTTP-прослойка.

API принимает POST-запрос на адрес:

```text
http://127.0.0.1:8080/command
```

Пример тела запроса для команды с ключом и значением:

```json
{
  "command": "SET",
  "key": "user",
  "value": "Alice"
}
```

API формирует команду для TCP-сервера, получает ответ и возвращает JSON.

Для команд без аргументов используется только поле `command`:

```json
{
  "command": "PING"
}
```

## 5. Реализация сайта

Статический сайт находится в папке `site`.

Основные страницы:

- `index.html` — главная страница.
- `about.html` — описание проекта.
- `journal.html` — журнал работы.
- `resources.html` — полезные материалы.
- `demo.html` — демонстрация работы Mini Redis Server.

Файл `site/script.js` отправляет запросы в HTTP API с помощью `fetch`.

## 6. Локальный запуск

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
cd site
python -m http.server 8000
```

После этого нужно открыть:

```text
http://127.0.0.1:8000/demo.html
```

## 7. Проверка

Проверку можно выполнить через сайт, CLI-клиент или HTTP API.

Через CLI:

```bash
python src/client.py SET test value
python src/client.py GET test
python src/client.py EXISTS test
python src/client.py UPDATE test updated
python src/client.py KEYS
python src/client.py LOG
python src/client.py DELETE test
python src/client.py FLUSH
```

Через HTTP API:

```bash
curl -X POST http://127.0.0.1:8080/command \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"GET\",\"key\":\"test\"}"
```
