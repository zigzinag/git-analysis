## Как запускать скрипт

Запуск скрипта с параметров:
```
>>> python git.py --repository https://github.com/apache/spark --branch branch-3.1 --since 2020-02-02 --until 2020-02-04
```
#Параметры:
  * по умолчанию значение branch = 'master'
  * значение since/until можно не задавать

Запуск скрипта без параметров:
```
>>> python git.py --repository https://github.com/apache/spark
```
