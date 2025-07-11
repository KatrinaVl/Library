# Library

Реализация RESTful API для базового управления библиотечным каталогом.

## Инструкция по запуску

1. Склонировать репозиторий

```
git clone git@github.com:KatrinaVl/Library.git
```
2. Перейти в папку library
```
cd library
```
3. Запустить команду

```
docker-compose up --build
```

После этого начнут подгружаться необходимые зависимости, и в конечном итоге будет запущен сервис.

#### Как зарегистрировать пользователя

Если необходимо зарегистрировать библиотекаря, то это делается через endpoint:
```
"http://0.0.0.0:8090/register"
```
Eсли необходимо зарегистрировать читателя, то это делает библиотекарь через endpoint:
```
"http://0.0.0.0:8090/add_reader" 
```

## Описание структуры проекта

Проект выглядит так:

```
.
├── README.md
└── library
    ├── alembic
    │   ├── Dockerfile
    │   ├── README
    │   ├── env.py
    │   ├── requirements.txt
    │   ├── script.py.mako
    │   ├── versions
    │   └── wait.sh
    ├── alembic.ini
    ├── api
    │   ├── Dockerfile
    │   ├── __init__.py
    │   ├── api.py
    │   ├── database.py
    │   ├── model.py
    │   ├── requirements.txt
    │   ├── tests
    │   │   ├── __init__.py
    │   │   ├── test_api_service.py
    │   │   └── test_business_logic.py
    │   └── wait.sh
    ├── book_service
    │   ├── Dockerfile
    │   ├── __init__.py
    │   ├── book_grpc.py
    │   ├── book_server.py
    │   ├── database.py
    │   ├── requirements.txt
    │   ├── start.sh
    │   └── tests
    │       ├── __init__.py
    │       └── test_book_service.py
    ├── docker-compose.yml
    └── proto
        ├── Dockerfile
        ├── __init__.py
        ├── book_service.proto
        ├── book_service_pb2.py
        ├── book_service_pb2_grpc.py
        └── requirements.txt
```

В папке library находится реализация сервиса. 

В папке alembic лежат версии миграций, а также все необходимые для Alembic файлы. 

Я решила отделить работу с книгами в отдельный сервис, который назвала book_service. Внутри одноименной папки лежат файлы для запуска gRPC-сервера, базы данных, описание класса gRPC и тесты.

Отдельно представлена папка proto, в которой лежат все необходимые файлы для protobuf.

В папке api непосредственно реализован основной сервис. В ней лежат файлы для базы данных библиотекарей и читателей, тесты, и реализация эндпоинтов приложения через FastAPI.

### Описание принятых решений в БД

Для начала, я решила использовать шаблоны таблиц, данные в задании. При этом я разделяю таблицы для библиотекарей и читателей, так как у них совершенно разные структуры. 

Также таблица читателей имеет дополнительную колонку ("count"), которая нужна для реализации бизнес-логики, чтобы отслеживать количество книг на руках у читателей.

Таблица с книгами также взяла структуру из задания. 

А вот для отслеживания процесса выдачи/принятия книг, я завела отдельную таблицу (BorrowedBooks), которая содержит в себе информацию о том, какой читатель взял книгу, какую взял книгу, когда взял и когда вернул (в целом структура взята из задания).

### Реализация бизнес-логики

#### Бизнес-логика 1 (количество экземпляров > 0)

Как я уже говорила, я отделила операции с книгами в отдельный сервис. Поэтому бизнес-логика 1 проверяется только там. В классе вызывается функция для работы с таблицей, внутри нее ищется нужная книга и проверяется, что она существует и количество экземпляров > 0. Возвращается bool значение, которое показывает: удалось взять книгу или нет. В api в методе "/give_book" вызывается первым gRPC метод, который как раз возвращает bool значение. Если удалось взять книгу, то уже дальше можно вносить запись в BorrowedBooks.

#### Бизнес-логика 2 (читатель не может взять больше 3-х книг одновременно)

Я поняла это таким образом, что читатель не может взять книгу, если он не вернул 3 и более книг.
Как я уже упоминала, для этого у каждого пользователя стоит счетчик книг, которые он не вернул. По этому количеству я определяю, может ли он взять еще книгу или нет.

Отдельно хотелось бы отметить, что если книга не выдана пользователю (например из-за ограничению в три книги), то снова вызывается gRPC метод, чтобы вернуть книгу. Это было одной из сложностей, с которой мне пришлось столкнуться. Однако аналогия схожа с реальной библиотекой, когда библиотекарю необходимо вернуть книгу обратно, если ее не получилось выдать.

#### Бизнес-логика 3 (читатель не может вернуть не ту книгу или уже возвращенную книгу)

Так как у меня есть таблица BorrowedBooks, то в запрос передавался borrowed_id. Однако еще необходимо иметь book_id книги, которую возвращают, ведь могут принести не ту книгу, что была в записи. Для пользователя я не делала такой проверки, так как обычно в библиотеках книгу может принести другой человек (например родственник).

Если пользователь пытается вернуть не ту книгу, то это просто обнаружится при сравнении book_id в записи и book_id книги. Также по записям можно посмотреть выставлена ли дата приема книги: если да - то будет возвращено оповещение, если нет - то книга будет возвращена.

#### Вывод всех книг

Вывод всех книг я решила сделать без аутентификации. Причиной такого решения было то, что любой пользователь вправе посмотреть наличие книги в бибилотеке и потом решить, стоит ли ему за ней идти.

Также я решила сделать вывод с пагинацией: когда либо пользователь, либо сама система решают сколько блоков информации приходится на страницу, и какую страницу нужно показать.

#### Вывод не возвращенных книг для каждого пользователя

Также применяется с пагинацией. Сначала вычисляется количество книг, которые пользователь не вернул, затем от них считается какие книги будут возвращены, список их id передается в gRPC-запросе, после чего сервис книг возвращает список книг по их id.

### Аутентификация

Для создания JWT токенов используется библиотека PyJWT, в основном из-за того, что я уже с ней работала. В файле library/api/api.py в самом начале реализованы две функции, одна из которых создает токен на определенное время (которое можно регулировать). В качестве ключа передается словарь:
``` 
{"librarian_id" : <librarian_id>}
```
Вторая функция расшифровывает этот токен и отдает полученный словарь. Если токен не подходит или истекло его время, то будет возвращено уведомление. После этого в таблице библиотекарей проверяется, что библиотекарь с таким id действительно существует.

Токен передается в заголовке, как это обычно и принято. Заголовок имеет вид:
```
Authorization: Bearer <token>
```

Почти все методы защищены JWT токенизацией, кроме регистрации нового библиотекаря ("/register") и его авторизации ("/login"). Также, как я упоминала, не защищен метод предоставления списка всех книг.

### Творческая часть (фича)

Я решила ориентироваться на реальную жизнь, чтобы новая фича была полезна. Обычно в библиотеках есть срок, в который книга должна быть возвращена. Те читатели, которые не вернули книгу в срок, выплачивают штраф. Соответственно, можно добавить функционал, который сможет вычислять должников, а также каждому пользователю выписывать его штраф, если он есть.

Для этого достаточно определить штраф и возможный срок владения книгой (например, 100 рублей за сутки).
После этого, когда человек возвращает книгу, достаточно вычислить, на сколько человек просрочил срок, после этого вычислить его штраф и добавить к текущей сумме.

С помощью этого библиотекари смогут также вычислять какие книги еще не вернули, сколько у них в библиотеке среди читателей штрафников и какая сумма штрафа должна быть возвращена.

Также следует установить временные границы, после истечения которых книга будет списана, как потерянная (например, год). После этого перестанет увеличиваться долг.


