# Django_tree_menu

Тестовое задание

## Задача

Нужно сделать django app, который будет реализовывать древовидное меню, соблюдая следующие условия:
1) Меню реализовано через template tag
2) Все, что над выделенным пунктом - развернуто. Первый уровень вложенности под выделенным пунктом тоже развернут.
3) Хранится в БД.
4) Редактируется в стандартной админке Django
5) Активный пункт меню определяется исходя из URL текущей страницы
6) Меню на одной странице может быть несколько. Они определяются по названию.
7) При клике на меню происходит переход по заданному в нем URL. URL может быть задан как явным образом, так и через named url.
8) На отрисовку каждого меню требуется ровно 1 запрос к БД

Нужен django-app, который позволяет вносить в БД меню (одно или несколько) через админку, и нарисовать на любой нужной странице меню по названию.

```{% draw_menu 'main_menu' %}```

При выполнении задания из библиотек следует использовать только Django и стандартную библиотеку Python.

## Quick run Example

### 1. Clone project
```commandline
git clone https://github.com/Fisherusby/django-tree-menu.git
```
### 2. Install requirements
```
pip install -r requirements.txt
```
### 3. Apply migrations
```
python manage.py makemigrations
python manage.py migrate
```
### 4. Create admin account
```
python manage.py createsuperuser
``` 
### 5. Initial data with examples for database
```
python manage.py loaddata tree_menu.json
``` 
### 6. Start server
```
python manage.py runserver
```
### 7. Examples
[Examples endpoint](http://127.0.0.1:8000/example/)

[Admin endpoint](http://127.0.0.1:8000/admin/)

## How use

1) Create Tree menu in admin panel.
2) Create Tree menu item. The url can absolute (http://127.0.0.1:8000/example/dasd) or path(/example/dasd) or named(news).
3) Insert template tag to your template:
```{% draw_menu 'main_menu' %}```

You can try this in example or add tree_menu app in your project.

Clone app in your project
```commandline
git clone https://github.com/Fisherusby/django-tree-menu.git tree_menu
```
Within settings.py, add ‘tree_menu’ to INSTALLED_APPS:
```
INSTALLED_APPS = (
    ...
    'tree_menu',
    ...
)
```
Make and apply migrations
```
python manage.py makemigrations tree_menu
python manage.py migrate tree_menu
```

