# Лабораторная работа: Оркестрация и автоматизация деплоя (Kubernetes & Helm)

## Описание проекта
Данный проект реализовывает отказоустойчивый счётчик количества посещений на сайте. 
Само веб приложение построено на базе:
- **Nginx** — *Reverse-Proxy* для обработки входящих запросов
- **Python** — Бэкенд сервис, отвечающий за логику сайта
- **Redis** — База данных для хранения количества посещений

## Как запустить локально
---
1. Клонируйте репозиторий
``` Bash
git clone https://github.com/George1109/ITMO-DevOps-Labs.git
cd Lab-2
```

2. Запустите minikube
``` Bash
minikube start -p <Имя_Кластера>
```

3. Проверьте статус Minikube
``` Bash
minikiube status
```

**1 Часть**
- Перейдите в нужную директорию
``` Bash
cd Part-1
```

- Запуск всех служб
``` Bash
kubectl apply -f .
```

- Проверьте статусы подов
``` Bash
kubectl apply -f .
```

- Запуск сайта
``` Bash 
minikube service nginx-service -p <Имя_Кластера>
```

**2 Часть**

- Перейдите в нужную директорию
``` Bash
cd Part-2
```

- Деплой чарт
``` Bash
helm install web-counter .
```

- Запуск сайта
``` Bash
minikube service nginx-service -p <Имя_Кластера>
```

## Почему Helm удобнее манифестов?
**1. Шаблонизация**

Меняем значение в values и оно меняется везде.

**2. История релизов**

Позволяет откатываться на нужную версию

**3. Сбор приложения в одно целое**

Одной командой можно проверить на ошибки и запустить проект.

## Примеры работы

![Part-1 working site](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/site-1.png)

Part-1 working site

![Part-1 working site 2](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/site-2.png)

Part-1 working site 2

![Part-1 Lens Overview](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/overview-Lens-3.png)

Part-1 Lens Overview

![Part-1 Lens Deployment](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/deployment-Lens-4.png)

Part-1 Lens Deployment

![Part-1 Lens Service](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/service-Lens-5.png)

Part-1 Lens Service

![Part-2 Chart Start](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/Chart-start-6.png)

Part-2 Chart Start

![Part-2 Helm Start](https://github.com/George1109/ITMO-DevOps-Labs/blob/919ed83e24c871a35f2bbb7319dc770df78c3313/Lab-2/pic/Helm-site-6.png)

Part-2 Helm Start
