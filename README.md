## Запуск приложения



1. Установить и активировать виртуальное окружение, установить зависимости
``` 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. В файле .evn заполнить необходимые данные
```
TOKEN = '<your token>'
```
3. Перейти в папку src 
``` 
cd src 
```
2. Запуск celery
```
celery -A distribution.task:celery worker --loglevel=INFO
```
3. Запуск flower
```
celery -A distribution.task:celery flower
```
4. Запуск приложения 
```
python main.py
```

http://0.0.0.0:8000/core/docs/ - документация проекта (OpenApi)
http://0.0.0.0:5555 - celery flower

