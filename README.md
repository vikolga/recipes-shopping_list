# praktikum_new_diplom

Сайт Foodgram, «Продуктовый помощник». 

Проект доступен по ссылке: http://foodgramov.hopto.org/

Для проверки:
- супер пользователь: vikolga
- пароль: 123qwe

Foodgram - проект позволяет:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок


Клонируйте репозитоий
```git clone git@github.com:vikolga/foodgram-project-react.git```

Проект использует базу данных PostgreSQL.
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

После создания образов можно создавать и запускать контейнеры.
Из папки "./infra/" выполнить команду:

```docker-compose up -d```

После успешного запуска контейнеров выполнить миграции:

```docker-compose exec backend python manage.py migrate```

Создать суперюзера (Администратора):

```docker-compose exec backend python manage.py createsuperuser```

Собрать статику:

```docker-compose exec backend python manage.py collectstatic --no-input```

Заполние базы данных:
- ингредиентами
```docker compose exec backend python manage.py load_ingredients```
- тегами
```docker compose exec backend python manage.py load_tags```


Техническая информация 
- Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

- Веб-сервер: nginx (контейнер nginx)
- Frontend фреймворк: React (контейнер frontend)
- Backend фреймворк: Django (контейнер backend)
- API фреймворк: Django REST (контейнер backend)
- База данных: PostgreSQL (контейнер db)

Автор: Викторова Ольга
