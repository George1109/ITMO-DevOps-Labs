# Лабораторная работа № 3: Nginx
## 1 Часть
## Описание проекта
Данный проект реализовывает развертывание 2 хостов на 1 сервере. Хосты принудительно перенаправляются на https
Проект выполнен на базе:
- **docker** — Развертываение контейнера с веб приложением
- **nginx** —  Веб сервер

## Как запустить локально
---
### Клонирование репозитория

``` Bash
git clone https://github.com/George1109/ITMO-DevOps-Labs.git
cd Lab-3
```

### Запуск

``` Bash
docker build -t <image_name> .
docker run --name <container_name> -d -p 80:8080 -p 443:443 <image_name>
```

Сайты site1.localhost и site2.localhost работают.
Примеры:

![Working site1](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/0.png)

Сайт №1

![Working site1](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/01.png)

Сайт №2

## 2 Часть

## Описание проекта
Попробовать взломать nginx любого доступного сайта. Проверить минимум три уязвимости.
Взлом считается успешным, если вы попали туда, куда не планировалось попадать пользователю, даже если там ничего нет.

### Directory listening
Это уязвимость, возникающая из-за неправильной настройки веб-сервера, которая позволяет пользователю просматривать список файлов и подпапок в директории при отсутствии в ней индексного файла.

![Directory listening](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/7.png)


### Path Traversal
Уязвимость, позволяющая злоумышленнику получить несанкционированный доступ к файлам и директориям на сервере, находящимся за пределами корневой папки веб-приложения. Результаты попыток:


![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/8.png)


![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/9.png)

### Fuzzing (ffuf)
Метод автоматизированного тестирования ПО, суть которого заключается в подаче на вход программе неправильных, неожиданных или случайных данных с целью вызвать сбой, зависание или утечку памяти.
Скачаем файлик common.txt который проверяет наличие совпадения названий директории на сайте со значением в файле. Примеры:

![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/1.png)

Проверим сайт azbez. Фаззинг показывает название + код доступа. Перейдем по директории со значением 200.

![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/2.png)

Скачаем файлик.

![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/3.png)

Выведем потенциально важные данные, надеясь, что это не honeypot :)

![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/3.png)

Пример фаззинга конкретной директории сайта

![Path Traversal](https://github.com/George1109/ITMO-DevOps-Labs/blob/c3e90b7fe4458077b65a4ca7f05caf982620f908/Lab-3/pic/3.png)

Найдена таблица сайта

Подводя итог, хочу подметить, что я не совсем понял смысл Path Traversal и Directory listening, потому что Fuzzing более сильный инструмент для поиска открытых путей на сайте.

