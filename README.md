# Foodgram

«Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

<p> Cостоит из бэкенд-приложения на Django и фронтенд-приложения на React. </p>

___
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=flat&logo=django&logoColor=white&color=ff1709&labelColor=light_grey)&nbsp;
![Django](https://img.shields.io/badge/DJANGO-1f6e4b.svg?&style=flat&logo=django&logoColor=white)&nbsp;
![SQLite](https://img.shields.io/badge/SQLITE-003B57.svg?&style=flat&logo=sqlite&logoColor=white)&nbsp;
![Python](https://img.shields.io/badge/PYTHON-3776AB.svg?&style=flat&logo=python&logoColor=white)&nbsp;
![react](https://img.shields.io/badge/-ReactJs-61DAFB?logo=react&logoColor=white&style=flat)&nbsp;
![Docker](https://img.shields.io/badge/DOCKER-2496ED.svg?&style=flat&logo=docker&logoColor=white)&nbsp;
![Nginx](https://img.shields.io/badge/NGINX-269539.svg?&style=flat&logo=nginx&logoColor=white)&nbsp;
![Postgres](https://img.shields.io/badge/POSTGRESQL-%23316192.svg?&style=flat&logo=postgresql&logoColor=white)&nbsp;
[![Django](https://img.shields.io/badge/Djoser-2.2.0-blue?)](https://djoser.readthedocs.io/en/latest/)


## Оглавление
1. [Описание](#описание)
2. [Стек технологий](##стек-технологий)
3. [Как запустить проект](##как-запустить-проект)
4. [Автор проекта](##автор-проекта)


### Описание

Foodgram - проект позволяет:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок

### Стек технологий

- Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.
- Веб-сервер: nginx (контейнер nginx)
- Frontend фреймворк: React (контейнер frontend)
- Backend фреймворк: Django (контейнер backend)
- API фреймворк: Django REST (контейнер backend)
- База данных: PostgreSQL (контейнер db)

### Как запустить проект

#### Запуск проекта локально:
Клонировать репозиторий:
```
git clone https://git@github.com:vikolga/recipes-shopping_list.git
```
В директории Recipe_publishing_network/backend создать и активировать виртуальное окружение:
```
python -m venv venv
Linux/macOS: source env/bin/activate
windows: source env/scripts/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r recipes-shopping_list/backend/requirements.txt
```
Выполнить миграции, создать суперюзера:
```
python manage.py migrate
python manage.py createsuperuser
```
#### Запуск проекта на удаленном сервере:
Подключиться к удаленному серверу и создать директорию foodgram:

```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
mkdir foodgram
```
Установка docker compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
В директорию foodgram/ скопируйте файл docker-compose.production.yml:
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```
Проект использует базу данных PostgreSQL.
В директории foodgram/ необходимо создать и заполнить ".env" с переменными окружения.
```
POSTGRES_DB=foodgram
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Секретный ключ'
ALLOWED_HOSTS='Имя или IP хоста'
DEBUG=True
DB_SQLITE=True
```
Запустите docker compose в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
Выполните миграции, загрузите данные в БД, соберите статику бэкенда и скопируйте их в /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata dump.json
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
На сервере в редакторе nano откройте конфиг Nginx:

sudo nano /etc/nginx/sites-enabled/default
Добавте настройки location в секции server:

location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:9000;
}
Проверьте работоспособность конфигураций и перезапустите Nginx:

sudo nginx -t 
sudo service nginx reload

#### Заполние базы данных:
- ингредиентами
```
docker compose exec backend python manage.py load_ingredients
```
- тегами
```
docker compose exec backend python manage.py load_tags
```

### Автор проекта
_[Викторова Ольга](https://github.com/vikolga)_, python-developer
