![workflow](https://github.com/Esperansa08/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) 

# сайт Foodgram «Продуктовый помощник»

### Содержание: 

- [сайт Foodgram «Продуктовый помощник»](#сайт-foodgram-продуктовый-помощник)
    - [Содержание:](#содержание)
    - [Краткое описание](#краткое-описание)
    - [Технологии](#технологии)
    - [Как запустить проект](#как-запустить-проект)
      - [Запуск проекта локально](#запуск-проекта-локально)
      - [Настройка проекта для развертывания на удаленном сервере](#настройка-проекта-для-развертывания-на-удаленном-сервере)
    - [Автор](#автор)
### Краткое описание 

На этом онлайн-сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект развернут на сервере: <http://esperansa.ddns.net/recipes/>

Документация к API находится по адресу:  <http://esperansa.ddns.net/api/docs/>


### Технологии 


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) 
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) 
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) 
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) 
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) 
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 


### Как запустить проект 

Клонировать репозиторий: 

``` 
git clone https://github.com/Esperansa08/foodgram-project-react.git
``` 

#### Запуск проекта локально 

1. Установите на сервере `docker` и `docker-сompose`. 
2. Создайте файл `/infra/.env`. Шаблон для заполнения файла нахоится в `/infra/example.env`. 
3. Выполните команду `sudo docker-compose up -d --buld`. 
4. Выполните миграции `sudo docker-compose exec backend python manage.py migrate`. 
5. Создайте суперюзера `sudo docker-compose exec backend python manage.py createsuperuser`. 
6. Соберите статику `sudo docker-compose exec backend python manage.py collectstatic --no-input`. 
7. При необходимости заполните базу `sudo docker-compose exec backend python manage.py loaddata fixtures.json`. 
8. Документация к API находится по адресу: <http://localhost/api/docs/>. 

#### Настройка проекта для развертывания на удаленном сервере 

1. Установите на сервере `docker` и `docker-dompose`. 
2. Локально отредактируйте файл `infra/nginx.conf`, в строке `server_name` впишите IP-адрес сервера. 
3. Скопируйте файлы `docker-compose.yaml` и `nginx/defult.conf` из директории `infra` на сервер: 
 
```bash 
    scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml 
    scp nginx.conf <username>@<host>:/home/<username>/nginx/default.conf 
``` 

4. Необходимо добавить Action secrets в репозитории на GitHub в разделе settings -> Secrets: 

* DOCKER_PASSWORD - пароль от DockerHub; 
* DOCKER_USERNAME - имя пользователя на DockerHub; 
* HOST - ip-адрес сервера; 
* SSH_KEY - приватный ssh ключ (публичный должен быть на сервере); 
* TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start) 
* TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота) 
* SECRET_KEY = секретный ключ проекта django 
* DB_ENGINE=django.db.backends.postgresql  
* DB_NAME=имя базы данных postgres 
* POSTGRES_USER=пользователь бд 
* POSTGRES_PASSWORD=пароль 
* DB_HOST=db 
* DB_PORT=5432 

5. Проверка работоспособности 

Теперь если внести любые изменения в проект и выполнить: 
``` 
git add . 
git commit -m "..." 
git push 

``` 
Комманда git push является триггером workflow проекта. 
При выполнении команды git push запустится набор блоков комманд jobs (см. файл yamdb_workflow.yaml). 
Последовательно будут выполнены следующие блоки: 
* tests - тестирование проекта на соответствие PEP8 и тестам pytest. 
* build_and_push_backend_to_docker_hub, build_and_push_frontend_to_docker_hub - при успешном прохождении тестов собирается образ (image) для docker контейнера  
и отправлятеся в DockerHub 
* Deploying on remote server - после отправки образа на DockerHub начинается деплой проекта на сервере. 
Происходит копирование следующих файлов с репозитория на сервер: 
  - docker-compose.yaml, необходимый для сборки трех контейнеров: 
    + postgres - контейнер базы данных 
    + web - контейнер Django приложения + wsgi-сервер gunicorn 
    + nginx - веб-сервер 
  - nginx/default.conf - файл кофигурации nginx сервера 
  - static - папка со статическими файлами проекта 
  После копировния происходит установка docker и docker-compose на сервере 
  и начинается сборка и запуск контейнеров. 
* Send Telegram message - после сборки и запуска контейнеров происходит отправка сообщения в  
  телеграм об успешном окончании workflow 
После выполнения всех шагов `workflow`, проект будет развернут на удаленном сервере. 

6. Для окончательной настройки, зайдите на уделенный сервер и выполните миграции, создайте суперюзера, 
соберите статику и заполните базу (см. шаги 4-7 из описания развертывания проекта на локальном сервере). 

### Автор 

 * Савельева Анастасия (Visteria09@yandex.ru, https://github.com/Esperansa08) 
 * Сайт: http://esperansa.ddns.net/api/