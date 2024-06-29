# Описание Pet-проекта Сайт «Прогноз температуры»

Инструкция по установке и использованию 

1. создайте на локальном компьютере каталог обмена, зайдите в него и выполните 
echo 0 > data_share_history.txt
echo 0 > data_share_future.txt

2. указывая для data_share_history.txt, data_share_future.txt полный путь в ОС, созданный в (1), установите контейнеры

docker run -d -it -p 8889:80 -v data_share_history.txt:/usr/share/nginx/html/data_history.txt:rw -v data_share_future.txt:/usr/share/nginx/html/data_future.txt:rw  --name=weather_yandex_web_server rus02/weather_yandex_web_server:0.1

docker run -d -it -p 3000:3000 -p 15432:5432 -v data_share_history.txt:/var/tmp/data_history_x.txt:rw -v data_share_future.txt:/var/tmp/data_future_x.txt:rw --name=weather_yandex_de_ml_server rus02/weather_yandex_de_ml_server:0.14


3. В UI Airflow http://localhost:3000/airflow/home запустить DAG weather_predict

Если после запуска в Airflow по пути http://localhost:3000/airflow/home
возникает сообщение:
The scheduler does not appear to be running.
The DAGs list may not update, and new tasks will not be scheduled.
==============================
Не является ошибкой проекта!!!
Администрирование Airflow не входит в курс DE, изучалось факультативно.
"По легенде" проекта, выполняю работу DevOps'а вместо сотрудника, уехавшего за пределы РФ и игнорирующего обращения коллег
==============================
выполнить внутри контейнера weather_yandex_de_ml_server команду
airflow scheduler
Для этого можно использовать терминалы в "Docker Desktop",  VSCode по адресу http://localhost:3000/vsc/?folder=%2Flessons%2F или командной строки

4. Поключение к метеосерверу (контейнер weather_yandex_web_server) доступно по адресу http://localhost:8889/
Сервер начнет показывать актуальную и историческую температуру и делать предсказания после накопления непрерывной (минимум 1р/час) истории наблюдения за 10ч.

5. Приятного использования !

### Описание DWH

Source
******
Public (доступ без УЗ)
host = https://rp5.ru/rss/5483/ru

XML-строка, исходные данные метеодатчиков
==========
Теги
----
https://ru.wikipedia.org/wiki/XPath
/feed/title - текст
название локации

/feed/updated - текст, приводится к timestamptz(0)
время обновления данных

/feed/entry/summary/span[@class="t_0"] - текст, некоторые значения приводятся к numeric(4,1), неприводимые значения нужно отбросить.
температуры отдельных датчиков, средняя температура (не доверяем, читаем всё и усредняем) и единицы измерения

далее
БД PostgreSQL
host=localhost:15432
УЗ=jovyan/jovyan

Stage
*****

rp5 таблица, исходные данные метеодатчиков. Очищается каждый раз перед добавлением данных.
===========
id serial4 NOT NULL rp5_pkey PRIMARY KEY
суррогатный ключ

region varchar(100) NULL
локация метеодатчиков

dt varchar(25) NULL
время сбора данных

t varchar(10) NULL
зафиксированная температура

DDS
***

regions таблица, все используемые локации
===============
id serial4 NOT NULL PRIMARY KEY
суррогатный ключ

region varchar(100) NOT NULL
название локации


temp таблица, зафиксированные температуры, очищено от нечисловых значений. Удаляются данные старше 1 недели
============
id serial4 NOT NULL PRIMARY KEY 
суррогатный ключ

region_id int4 NOT NULL
id локации, внешний ключ на dds.regions

dt timestamptz(0) NOT NULL
время фиксации температуры, приведено к timestamptz(0) и построен индекс для выполнения группировок

t numeric(4, 1) NOT NULL
зафиксированная температура


MART
****
regions таблица, все используемые локации. Полностью перегружается данными DDS.regions
===============
id serial4 NOT NULL PRIMARY KEY
суррогатный ключ

region varchar(100) NOT NULL
название локации


avg_temp таблица, усредненная температура, полученная за час в данной локации. Полностью пересчитывается из dds.temp 
================
id serial4 NOT NULL PRIMARY KEY 
суррогатный ключ

region_id int4 NOT NULL
id локации, внешний ключ на mart.regions

dt timestamptz(0) NOT NULL
время фиксации температуры без минут-секунд и построен индекс для выполнения поиска

t numeric(4, 1) NOT NULL
усредненная температура

ml_data представление, исторические данные температу. Для визуализации и построения прогноза. Строится на основе mart.regions и mart.avg_temp
=====================
region varchar
наименование локации

dt_max timestamptz(0)
время последнего замера без минту-секунд для данной локации

m0 - 0/1
признак зимнего месяца

m1 - 0/1
признак весеннего месяца

m2 - 0/1
признак летнего месяца

m3 - 0/1
признак осеннего месяца

hh - int
час 9 часов до dt_max 

t3 - float
температура в час hh

t2 - float
температура в час hh+3ч

t1 - float
температура в час hh+6ч

t0 - float
температура в час dt_max (он же hh+9ч)


data_share_history.txt файл, температура за последний час и три предыдущих усредненных показания с интервалом 3ч
===========================
1 строка  : наименование локации
2-5 строки: дата (в формате ГГГГ-ММ-ДД ЧЧ:00) и температура (градусы Цельсия)


data_share_future.txt файл, 4 прогноза температура с интервалом 3ч
==========================
1 строка  : наименование локации
2-5 строки: дата (в формате ГГГГ-ММ-ДД ЧЧ:00) и температура (градусы Цельсия)


### Описание файлов проекта


ReadMe.md - этот файл, состоит из :
Описание действий для установки и использования
Описание SQL-скриптов и объектов БД
Описание файлов проекта

DOC
Каталог с описаниями

DOC\DE_Yandex_2023-2024.pptx она же DE_Yandex_2023-2024.pdf
Презентация дипломного проекта курса DE ЯндексПрактикума

DOC\BMSTU_ML_2022_JRG.pptx
Презентация используемых в проекте элементов ML прошлого курса обучения

DOC\Dobro.jpg
согласование начала работ

WORK
Каталог с рабочими материалами

WORK\rp5.xml
Пример данных погоды, получаемых с сервера

WORK\Черновик
какие-то записки

WORK\doker
Каталог с материалами создания Docker-образов

WORK\doker\weather_yandex_de_ml_server
Каталог с материалами создания Docker-образа подготоки данных

WORK\doker\weather_yandex_de_ml_server\Dockerfile
Сценарий создания Docker-образа подготоки данных

WORK\doker\weather_yandex_de_ml_server\cr.bat
Командный файл для создания и публикации. Использовать с парамтером "tag", ранее использовалось: cr.bat 0.14

WORK\doker\weather_yandex_de_ml_server\dag.py
DAG получения исходных значений температуры их обработки и построения прогноза. Импортируется в контейнер на этапе сборки

WORK\doker\airflow.cfg и airflow-2-2-3.cfg
подменяемые файлы конфигурации Airflow с измененными параметрами:
executor = LocalExecutor
dags_are_paused_at_creation = False

WORK\doker\weather_yandex_de_ml_server\ml
Каталог с экспортированными ML-объектами. Все объекты импортируются в контейнер на этапе сборки

WORK\doker\weather_yandex_de_ml_server\ml\lr1.sav
Прогноз на 3ч.

WORK\doker\weather_yandex_de_ml_server\ml\lr2.sav
Прогноз на 6ч.

WORK\doker\weather_yandex_de_ml_server\ml\lr3.sav
Прогноз на 9ч.

WORK\doker\weather_yandex_de_ml_server\ml\lr4.sav
Прогноз на 12ч.

WORK\doker\weather_yandex_de_ml_server\ml\X_scale.sav
Нормирование вектора исходных значений

WORK\doker\weather_yandex_de_ml_server\ml\y_scale.sav
Нормирование вектора результирующих значений (здесь используется для восстановления значения тепературы до естественных показаний)

WORK\doker\weather_yandex_de_ml_server\sql
Каталог с sql-скриптами для выполнения во встроенной БД PostgreSQL. Все объекты импортируются в контейнер на этапе сборки.
Подробнее, см. ReadMe_SQL.txt

WORK\doker\weather_yandex_de_ml_server\sql\init_db.sql
Скрипты пересоздания рабочих схем и создания всех объектов БД.
ВЫПОЛНЯЕТСЯ на этапе сборки контейнера!!!

WORK\doker\weather_yandex_de_ml_server\sql\init_stg.sql
Очистка таблицы слоя STAGE перед загрузкой новой порции данных, выполняется из DAGа

WORK\doker\weather_yandex_de_ml_server\sql\insert_DDS_with_DQ.sql
Перегрузка данных из STAGE в DDS слой, выполняется из DAGа

WORK\doker\weather_yandex_de_ml_server\sql\insert_MART_with_AVG.sql
Перегрузка данных из DDS в MART слой, выполняется из DAGа

WORK\doker\weather_yandex_web_server
Каталог с материалами создания Docker-образа отображения данных

WORK\doker\weather_yandex_web_server\cr.bat
Командный файл для создания и публикации. Использовать с парамтером "tag", ранее использовалось: cr.bat 0.1

WORK\doker\weather_yandex_web_server\Dockerfile
Сценарий создания Docker-образа подготоки данных

WORK\doker\weather_yandex_web_server\index.html
Веб-страница визуализации истории и прогноза температуры, импортируется в контейнер на этапе сборки

WORK\doker\weather_yandex_web_server\pet.png
Позитивная картинка для веб-страницы, импортируется в контейнер на этапе сборки

WORK\Pic
Каталог с рабочими картинками













