# My Cloud — BAKEND  
  
Репозиторий содержит серверную часть веб-приложения на базе фреймворка Django (Python).   

---  
  
## ☁️ Структура проекта  
*   `my_project_jango/` - основная папка конфигурации Django проекта.  
    *   `settings_local.py` - базовые настройки проекта (для разработки, DEBUG=True).  
    *   `settings_production.py` - настройки для продакшн-сервера.  
    *   `urls.py` - главный маршрутизатор запросов.  
*   `storage/` - папка по управлению хранилищем приложения
	*   `admin.py` - регистрация модели File
	*   `apps.py` - конфигурация и метаданные приложения storage
    *   `models.py` - описание модели File
    *   `serializers.py` - сериализатор модели File
    *    `urls.py` - маршрутизаторы запросов обработчиков приложения
    *    `views.py` - обработчики:
	     * загрузка файлов
	     * просмотр файлов
	     * удаление файлов
	     * переименование файлов
	     * скачивание файла
	     * формирование спец ссылки
	     * скачивание по спец ссылке в тч внешними неавторизованными пользователями
*   `<users>/` — папка папка по управлению пользователями приложения
	*   `admin.py` - регистрация модели User
	*   `apps.py` - конфигурация и метаданные приложения users
    *   `models.py` - описание модели User
    *   `serializers.py` - сериализатор модели User
    *    `urls.py` - маршрутизаторы запросов обработчиков приложения
    *    `views.py` - обработчики:
	     * регистрация
	     * логин
	     * логаут
	     * получение списка юзеров (только админ)
	     * удаление юзера (только админ)
	     * изменение значения признака “администратор” (только админ)
*   `<tests>/` — папка c тестами API части для users/.  
*   `media/` — директория для пользовательских загружаемых медиа-файлов (изображений).  
*   `requirements.txt` — список зависимостей проекта.  
*   `manage.py` — утилита командной строки Django для управления проектом.  
  
---  
  
## ☁️ Инструкция по общему развёртыванию приложения  
  
Приложение разворачивается на сервере Ubuntu с использованием связки Gunicorn, Nginx и окружения Python.  

### Предварительные требования 
- Ubuntu 22.04+
- Python 3.10+
- PostgreSQL 14+
- Node.js 20+
- Nginx

### Ссылки на репо
- Backend: https://github.com/Anastas0812/back-MYCLOUD
- Frontend: https://github.com/Anastas0812/front-MYCLOUD

### Открытые порты
На сервере должны быть открыты порты: 
- 80 (HTTP) 
- 22 (SSH)

### Шаг 0. Подготовка сервера
1. Создайте системного пользователя:
``adduser ваш_юзер ``
``usermod ваш_юзер -aG sudo``

2. Установите необходимые пакеты:
``sudo apt update``
``sudo apt install python3-venv python3-pip postgresql nginx``

### Настройка базы данных
1. Создайте базу данных и пользователя:
``sudo -u postgres psql``
``CREATE DATABASE my_cloud;``
 ``ALTER USER postgres WITH PASSWORD 'ваш_пароль_бд'; ``
 ``\q``

### Настройка переменных окружения
Для управления конфигурацией приложение использует пакет python-dotenv. 
В коде инициализация выглядит следующим образом:
```python
from dotenv import load_dotenv
load_dotenv()
```

Создайте файл `.env` в корне проекта (`/home/ваш_юзер/back-MYCLOUD/.env`):
``DB_NAME=my_cloud``
``DB_USER=postgres ``
``DB_PASSWORD=ваш_пароль_бд ``
``DB_HOST=localhost ``
``DB_PORT=5432 ``
``SECRET_KEY=ваш_секретный_ключ #мин. 50 символов``
*рекомендуется использовать генератор ключей, например https://djecrety.ir/*
``DEBUG=False``

### Создание суперпользователя
``python manage.py createsuperuser``
После создания установите флаг `is_admin=True`:
``python manage.py shell``
``from users.models import User`` 
``user = User.objects.get(username='ваш_логин')`` 
``user.is_admin = True user.save()`` 
``exit()``

### Настройка Gunicorn
Создайте файл `/etc/systemd/system/gunicorn.service`:
``[Unit] ``
``Description=Gunicorn ``
``MyCloud After=network.target ``

``[Service] ``
``User=ваш_юзер ``
``Group=www-data ``
``WorkingDirectory=/home/ваш_юзер/back-MYCLOUD ````ExecStart=/home/ваш_юзер/back-MYCLOUD/env/bin/gunicorn \ ``
``my_project_jango.wsgi:application \ ``
``--bind 127.0.0.1:8000 \ ``
``--workers 3 ``
``Restart=always``
``RestartSec=5``

``[Install]``
``WantedBy=multi-user.target``

### Настройка Nginx
Создайте файл `/etc/nginx/sites-available/mycloud`:
``server { ``
		``listen 80;``
		``server_name ВАШ-IP; ``
		``client_max_body_size 100M; ``
	``location / { ``
		``root /home/ваш_юзер/front-MYCLOUD/dist;`` 
		``index index.html;`` 
		``try_files $uri $uri/ /index.html;``
	``}``
``location /api/ {``
	``proxy_pass http://127.0.0.1:8000;`` 
	``proxy_set_header Host $host;`` 
	``proxy_set_header X-Real-IP $remote_addr;`` 
``}`` 
	``location /media/ {`` 
		``alias /home/ваш_юзер/back-MYCLOUD/media/;``
	`` }`` 
		``location /static/ {`` 
			``alias /home/ваш_юзер/back-MYCLOUD/staticfiles/; ``
		``}`` 
	``}``

``sudo ln -s /etc/nginx/sites-available/mycloud /etc/nginx/sites-enabled/``
``sudo nginx -t sudo systemctl restart nginx``

### Права доступа

``chmod 755 /home/ваш_юзер ``
``chmod -R 755 /home/ваш_юзер/front-MYCLOUD/dist ``
``chmod -R 755 /home/ваш_юзер/back-MYCLOUD/staticfiles ``
``chmod -R 755 /home/ваш_юзер/back-MYCLOUD/media``

### Известные особенности

- Папка `logs/` создаётся вручную: `mkdir logs && touch logs/app.log` 
- `media/`, `logs/`, `.env` не хранятся в git — создаются на сервере вручную
- Копирование ссылки работает только на HTTPS — на HTTP используется запасной метод через `execCommand` (handleCopyLink)
- Загрузка файлов ограничена 100МБ (настраивается в Nginx client_max_body_size  100M;)

### Шаг 1. Подготовка и сборка Фронтенда  
Перед запуском бэкенда необходимо подготовить артефакты фронтенда. Инструкция по сборке статических файлов находится в README.md репозитория фронтенда.   
После сборки артефакты (папка `dist`) должны быть размещены на сервере по пути, доступному веб-серверу Nginx (например, `/home/ваш_юзер/front-MYCLOUD/dist`).  
  
### Шаг 2. Развёртывание бэкенда на сервере  
1. Клонируйте репозиторий бэкенда в домашнюю директорию:  
    ``cd ~`` 
    ``git clone <ссылка_на_гитхаб_бэкенда> back-MYCLOUD ``
    ``cd back-MYCLOUD ``
2. Создайте и активируйте виртуальное окружение Python:
``python3 -m venv env``
``source env/bin/activate``
3. Установите необходимые зависимости:
``pip install -r requirements.txt``
4. Выполните миграции базы данных и соберите статику Django:
``python manage.py migrate``
``python manage.py collectstatic --noinput``

### Шаг 3. Настройка и запуск сервисов
1. **Gunicorn:** Настройте системную службу `systemd` (например, `/etc/systemd/system/gunicorn.service`) для управления процессом Django. Запустите сервис:
``sudo systemctl daemon-reload``
``sudo systemctl start gunicorn``
``sudo systemctl enable gunicorn``

2. **Nginx:** Настройте конфигурационный файл веб-сервера (в `/etc/nginx/sites-available/`). Пропишите:

-   Раздачу статики фронтенда из папки `dist`.
-   Проксирование запросов к API (`/api/` или `/admin/`) на сокет/порт Gunicorn.

3. Перезапустите Nginx:
``sudo systemctl restart nginx``
