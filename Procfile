release: python manage.py migrate
web: daphne test_cs.asgi:application --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=test_cs.settings -v2