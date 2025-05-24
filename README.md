# Lu Estilo API

API RESTful desenvolvida para a Lu Estilo, uma empresa de confecção, utilizando FastAPI.

## Tecnologias Utilizadas

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Poetry (Gerenciador de Dependências)
- Docker
- Pytest

## Estrutura do Projeto

```
app-estilo/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   ├── alembic/
│   ├── .env.example
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── pyproject.toml
```

## Configuração do Ambiente

1. Clone o repositório
2. Instale as dependências:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

4. Execute as migrações do banco de dados:
```bash
alembic upgrade head
```

5. Inicie a aplicação:
```bash
poetry run uvicorn app.main:app --reload
```

## Migrações de Banco de Dados

Para criar scripts de migração automaticamente a partir dos modelos SQLAlchemy:

1. **Gerar uma nova migração automaticamente:**
   ```bash
   poetry run alembic revision --autogenerate -m "mensagem_da_migracao"
   ```
   Substitua `mensagem_da_migracao` por uma descrição da alteração.

2. **Aplicar as migrações ao banco de dados:**
   ```bash
   poetry run alembic upgrade head
   ```

> **Observação:**
> O Alembic está configurado para detectar automaticamente as mudanças nos modelos. Sempre que criar ou alterar modelos, gere uma nova migração antes de aplicar.

## Documentação da API

A documentação da API estará disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testes

Para executar os testes:
```bash
poetry run pytest
```

## Docker

Para executar com Docker:
```bash
docker-compose up --build
``` 