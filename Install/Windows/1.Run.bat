docker run -d -it -p 8889:80 ^
-v C:\Work\PetProjJRG\data_share_history.txt:/usr/share/nginx/html/data_history.txt:rw ^
-v C:\Work\PetProjJRG\data_share_future.txt:/usr/share/nginx/html/data_future.txt:rw  ^
--name=weather_yandex_web_server rus02/weather_yandex_web_server:0.1

docker run -d -it -p 3000:3000 -p 15432:5432 ^
-v C:\Work\PetProjJRG\data_share_history.txt:/var/tmp/data_history_x.txt:rw ^
-v C:\Work\PetProjJRG\data_share_future.txt:/var/tmp/data_future_x.txt:rw ^
--name=weather_yandex_de_ml_server rus02/weather_yandex_de_ml_server:0.7
