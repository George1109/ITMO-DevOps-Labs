# Лабораторная работа 5: Мониторинг в Kubernetes с использованием Prometheus и Grafana

## Описание проекта
Данный проект реализовывает мониторинг за сервисом, поднятом в k8s через Grafana. 

Технологии:
- **Kubernetes**
- **Prometheus**
- **Grafana**

## Как запустить локально
---
1. Клонируйте репозиторий
``` Bash
git clone https://github.com/George1109/ITMO-DevOps-Labs.git
cd Lab-5
```

2. Запустите minikube
``` Bash
minikube start -p <Имя_Кластера>
```

3. Проверьте статус Minikube
``` Bash
minikiube status
```

4. Деплой чарт
``` Bash
helm install web-counter .
```

5. Запуск сайта
``` Bash
minikube service nginx-service -p <Имя_Кластера>
```

6. Запуск веб интерфейса для мониторинга
``` Bash
minikube service my-prometheus-grafana -p  <Имя_Кластера>
```
---

## Настройки мониторинга
1. Копируем лабораторную работу №2
<img width="1710" height="1011" alt="Снимок экрана — 2026-05-26 в 09 27 09" src="https://github.com/user-attachments/assets/b96bfa26-4bbd-418a-b3cb-513b853d2581" />

2. Устанавливаем официальный стек

``` Bash
helm install my-prometheus prometheus-community/kube-prometheus-stack \
  --set prometheus.prometheusSpec.service.type=NodePort \
  --set prometheus.prometheusSpec.service.nodePort=30010 \
  --set grafana.service.type=NodePort \
  --set grafana.service.nodePort=30020
```

3. Проверяем установку (смотрим поды)

<img width="1497" height="359" alt="Снимок экрана — 2026-05-26 в 12 03 14" src="https://github.com/user-attachments/assets/32d46de2-5019-4441-9b81-e68f6893be0f" />

4. Запускаем сайт

<img width="841" height="983" alt="Снимок экрана — 2026-05-26 в 12 10 22" src="https://github.com/user-attachments/assets/dfed18fd-0fab-46a1-8460-697d0f787541" />

5. Смотрим логин и пароль в секретах

<img width="1504" height="462" alt="Снимок экрана — 2026-05-26 в 12 17 58" src="https://github.com/user-attachments/assets/deb31922-24fa-4eb9-a384-ee2d6049456a" />

6. Готово! Смотрим всё, что нам нужно

<img width="848" height="1008" alt="Снимок экрана — 2026-05-26 в 12 06 57" src="https://github.com/user-attachments/assets/b76eda15-11b0-4fa4-965f-a56882c9c9c3" />
<img width="822" height="985" alt="Снимок экрана — 2026-05-26 в 12 20 26" src="https://github.com/user-attachments/assets/5245509f-dd6b-4204-a79a-83d0dcf009e5" />
<img width="831" height="991" alt="Снимок экрана — 2026-05-26 в 12 18 43" src="https://github.com/user-attachments/assets/56a43383-dd69-43ac-8b55-59afd773c448" />

