# 🛡️ SentinelOne Alerts Bot

Bot de Python + Docker para monitorear **una o más consolas de SentinelOne** y enviar alertas automáticamente a un canal de **Discord**.

---

## 📦 Características

- Monitorea múltiples consolas SentinelOne en paralelo 🧠
- Envía alertas detalladas a Discord 🚨
- Evita alertas duplicadas (persistencia de IDs detectados)
- Contenedor Docker listo para producción 🐳
- Configuración por variables de entorno (.env)

---

## 📁 Estructura del proyecto

```
ALERTAMIENTO/
├── data/
│   ├── seen_ids_1.json     # IDs vistos de consola 1 (se crea automáticamente)
│   ├── seen_ids_2.json     # IDs vistos de consola 2 (se crea automáticamente)
├── app.py                  # Código principal del bot
├── requirements.txt        # Dependencias de Python
├── Dockerfile              # Imagen de Docker
├── compose.yml             # Docker Compose
├── .env                    # Variables de entorno (NO se sube al repo)
```

---

## 🛠️ Requisitos

- Docker
- Docker Compose
- Python (si lo ejecutás local sin Docker)

---

## 🧪 Configuración (.env)

Crea un archivo `.env` en la raíz con lo siguiente:

```env
# Primera consola SentinelOne
S1_CONSOLE_1=https://console1.sentinelone.com
S1_TOKEN_1=tu_token_1

# Segunda consola SentinelOne
S1_CONSOLE_2=https://console2.sentinelone.com
S1_TOKEN_2=tu_token_2

# Webhook de Discord
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# Intervalo entre chequeos (en segundos)
INTERVAL=300
```

> 📝 Podés agregar más consolas duplicando el patrón y editando la variable de CONSOLES en `app.py`.

---

## 🚀 Cómo levantar el proyecto

### 1. Clona el repositorio y entra al directorio:

```bash
git clone https://github.com/brandugar/alertamiento_S1_Discord.git
cd alertamiento_S1_Discord
```

### 2. Crea el archivo `.env`.

```bash
touch .env
```

Edita `.env` con tu información real.

### 3. Construye y levanta el contenedor

```bash
docker compose build
docker compose up -d
```

### 4. Verifica los logs

```bash
docker logs -f s1-alerts-bot
```

Deberías ver algo como:

```
📡 Monitoreando https://console1.sentinelone.com cada 300 segundos...
📡 Monitoreando https://console2.sentinelone.com cada 300 segundos...
```

---

## 📤 ¿Qué envía a Discord?

Cuando encuentra una amenaza no resuelta (`incidentStatus == "unresolved"`), envía algo como:

```
🚨 Alerta SentinelOne
💼 Cliente: {cliente}
🖥️ Host: 'LAPTOP-PEPE'
🦠 Amenaza: 'HackTool.Win32'
🔍 Proceso Originador: 'powershell.exe'
📊 Clasificación: 'Malicious'
🔒 Confianza: 'High'
```

---

## 🧼 Limpieza

Para parar y eliminar todo:

```bash
docker compose down
```

---

## 🛡️ Seguridad

Este bot **no hace cambios ni acciones** sobre la consola, solo **lee alertas** vía API. Tus tokens deben mantenerse seguros y no subirse a ningún repositorio público.

---

## 🧙 Autor

Hecho con cariño por brandugar Δ.

---
