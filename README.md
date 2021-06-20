# Дипломный проект по курсу «Django: создание функциональных веб-приложений»

API сервиса интернет-магазин с интерфейсом администрирования.
Используемый фреймворки Django и Django REST Framework.


## Описание API

Сущности:

### Товар

url: `/api/v1/products/`

Поля:

- название
- описание
- цена
- дата создания
- дата обновления

Доступные действия: retrieve, list, create, update, destroy.

Создавать товары могут только админы. Смотреть могут все пользователи.

Должна быть возможность фильтровать товары по цене и содержимому из названия / описания.

### Отзыв к товару

url: `/api/v1/product-reviews/`

- ID автора отзыва
- ID товара
- текст
- оценка от 1 до 5
- дата создания
- дата обновления

Доступные действия: retrieve, list, create, update, destroy.

Оставлять отзыв к товару могут только авторизованные пользователи. 1 пользователь не может оставлять более 1го отзыва.

Отзыв можно фильтровать по ID пользователя, дате создания и ID товара.

Пользователь может обновлять и удалять только свой собственный отзыв.

### Заказы

url: `/api/v1/orders/`

- ID пользователя
- позиции: каждая позиция состоит из товара и количества единиц
- статус заказа: NEW / IN_PROGRESS / DONE
- общая сумма заказа
- дата создания
- дата обновления

Доступные действия: retrieve, list, create, update, destroy.

Создавать заказы могут только авторизованные пользователи. Админы могут получать все заказы, остальное пользователи только свои.

Заказы можно фильтровать по статусу / общей сумме / дате создания / дате обновления и продуктам из позиций.

Менять статус заказа могут только админы.


### Подборки

url: `/api/v1/product-collections/`

- заголовок
- текст
- товары в подборке
- дата создания
- дата обновления

Доступные действия: retrieve, list, create, update, destroy

Создавать подборки могут только админы, остальные пользователи могут только их смотреть.


## Интерфейс администратора

* Редактирование и просмотр подборок.
* Редактирование и просмотр товаров.
* Просмотр списка заказов пользователей, отсортированных по дате создания, с указанием пользователя и количества товаров.
* Страница детализации заказа с просмотром списка заказанных товаров.
* Редактирование и просмотр отзывов.


## Организация системы

* Система реализована на Django 3.
* Интерфейс администратора создан стандартными средствами Django admin.
* В качестве СУБД используется Postgresql.

## Документация по проекту

Для запуска проекта необходимо:

Установить зависимости:

```bash
pip install -r requirements-dev.txt
```

Необходимо создать базу в postgres, добавить в настройки проекта и прогнать миграции:

```base
manage.py migrate
```

Для заполнения БД тестовыми данными выполните команду:
```base
manage.py loaddata fixtures.json
```

Выполнить команду для тестирования API:

```bash
pytest
```

Примеры с запросами находятся в папкe```request_examples``` в корне проекта. В примерах отсутствуют запросы 
с невалидными данными. Проверка на валидность есть в тестах.


