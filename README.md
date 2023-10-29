# Проект foodgram
## Описание проекта
Проект позволяет объединить в одном месте рецепты разных пользователей, с возможностью создавать и выкладывать собственные рецепты, добавлять рецепты других пользователей в избранное и список покупок. Помимо этого, есть возможность подписаться на автора рецептов и следить за новыми публикациями.

## Как подготовить и запустить проект
1. [Подготовка к установке Docker](#title1)
2. [Установка Docker](#title2)
3. [Настройка проекта перед запуском](#title3)
4. [Запуск проекта](#title4)

### <a id="title1">1. Подготавливаем Windowns к установке докера</a>
    Установите Windows Subsystem for Linux (WSL) или Разверните виртуальную машину с Linux или настройте гипервизор Hyper-V.

    Для Windows 10 и 11: ставим Windows Subsystem for Linux
    Установите Windows Subsystem for Linux по инструкции с официального сайта Microsoft:
    https://docs.microsoft.com/ru-ru/windows/wsl/install-win10

### <a id="title2">2. Устанавливаем докер</a>
    `sudo apt update` - Обновите репозиторий пакетов для установки в Ubuntu
    `sudo apt install curl` - Установите консольную утилиту, которая умеет скачивать файлы по команде пользователя

    `curl -fSL https://get.docker.com -o get-docker.sh` - С помощью утилиты curl скачайте скрипт для установки докера с официального сайта

    `sudo sh ./get-docker.sh` - Запустите сохранённый скрипт с правами суперпользователя

    `sudo apt-get install docker-compose-plugin` - Дополнительно к Docker установите утилиту Docker Compose

    `sudo systemctl status docker` - Проверьте, что Docker работает

    Также, скачайте версию Desktop: https://www.docker.com/products/docker-desktop

### <a id="title3">3. Настраиваем проект перед запуском</a>

    В корне проекта создайте файл .env и добавьте в него переменные для Django-проекта:

    ```
    # Переменные для postgres:
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=mysecretpassword
    POSTGRES_DB=django
    # Добавляем переменные для Django-проекта:
    DB_HOST=db
    DB_PORT=5432

    SECRET_KEY=<Ваш secret_key django-проекта>
    DEBUG=False
    CSRF_TRUSTED_ORIGINS=<ваши домены и ip-адреса>
    ALLOWED_HOSTS=<ваши домены и ip-адреса>
    ```

### <a id="title4">4. Запуск проекта</a>
    Перейдите в директорию infra и выполните команду:

    `docker compose up`

    Проверьте работу сайта по вашему домену
