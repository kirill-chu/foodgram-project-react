[![foodgram workflow](https://github.com/kirill-chu/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/kirill-chu/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

# foodgram

Учебный проект от яндекс.практикум. Спринт 13.
- Развернутый проект доступен по адресу: http://158.160.75.41
- Документация API доступна: http://158.160.75.41/api/docs/
- Админка доступна по адресу: http://158.160.75.41/admin

### Как запустить проект на тестовом сервере django:
- Клонировать репозиторий и перейти в него в командной строке.
- Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv 
source env/bin/activate
```

- Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

- Выполнить миграции:
```
python3 manage.py migrate
```

-  Создать супер-пользователя для администоирования
```
python3 manage.py createsuperuser
```

- Заполните таблицу ингредиентов выполнив команнду
```
python3 manage.py fillingredients
```

- Запустить проект:
```
python3 manage.py runserver 0:8000
```
- Для администрирования пройдите по ссылке `http://localhost:8000/admin/` и воспользуйтесь ранее созданной учетной записью супер-пользователя.


### Как запустить проект в контейнере
- Клонировать репозиторий и перейти в него в командной строке.
- Перейдите в дирректоию `infra` в ней располагается `docker-compose.yaml` файл.
- В дирректории выполните команду
```
sudo docker-compose up -d
```
Проект запущен и готов, но для полноценной работы выполните миграции и предварительные настройки. В зависимости от версий установленных пакетов используйте команду `docker compose` или `docker-compose`:
```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py fillingredients
```
- Для администрирования пройдите по ссылке `http://localhost/admin/` и воспользуйтесь ранее созданной учетной записью супер-пользователя.


### Настройки для подключения к базе данных
В директории infra создайте файд `.env` `example.env` внесите в него необходимые учетные данные для подключения к БД и пересобирите проект при необходимости.

Шаблон `.env`
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 

Для остановки сервисов и удаления контейнеров выполните команду:
```
sudo docker-compose down -v
```

```
Для пересборки проекта используйте команду:
```
sudo docker-compose -up -d --build
```
### Прочие настройки файла `.env`
```
SECRET_KEY = "" # укажите SECRET_KEY Django проекта
DEBUG = "false" # Включение debug режима
ALLOWED_HOSTS = "host1 host2" # Перечислите через пробел хосты или их IP адреса
```
Для генерации `SECRET_KEY` воспользуйтесь командой функцией `get_random_secret_key(), например:

```
sudo docker-compose exec backend python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Deploy при помощи git actions
- Форкните проект.
- Подготовьте сервер для деплоя.
Установить на него docker.io и docker compose официальная документация доступна здесь: https://docs.docker.com/compose/install/
Скопируйте все каталоги `infra`, `frontend`, `docs` в `home/<ваш_username>/` на подготовленном сервере.
Создайте необходимые secrets в проекте на github, которые встречаются в `yamdb_workflow.yml`.
После пуша в ветку `main` будет происходить yamdb_workflow деплой, и телеграм оповещение.
