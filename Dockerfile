FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry
RUN poetry config virtualenvs.create false

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 