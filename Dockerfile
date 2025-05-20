FROM python:3.11-slim

# Установим зависимости для Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установим Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

# Установим зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем фронтенд
COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Копируем бэкенд
COPY App /app/App
COPY render.yaml /app/render.yaml

# Установим зависимости для фронтенда
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Установим pm2 для запуска обоих приложений
RUN npm install -g pm2

# Настроим pm2 для запуска обоих приложений
WORKDIR /app
COPY ecosystem.config.js .

EXPOSE 3000

CMD ["pm2-runtime", "start", "ecosystem.config.js"]
