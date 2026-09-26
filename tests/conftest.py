import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.db.session import get_async_db

# 1. Spin up PostgreSQL Docker Container
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        postgres.start()
        yield postgres

@pytest.fixture(scope="session")
def db_url(postgres_container):
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.username
    password = postgres_container.password
    db = postgres_container.dbname
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

# 2. Initialize Database Engine & Schemas
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database(db_url):
    engine = create_async_engine(db_url, echo=False)
    
    # Create multi-tenant schemas and tables
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "tenant_alpha"'))
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "tenant_beta"'))
        
        # Create patients table inside both schemas
        for schema in ["tenant_alpha", "tenant_beta"]:
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}".patients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                )
            """))

    yield
    await engine.dispose()

# 3. Async DB Session Override for FastAPI
@pytest_asyncio.fixture
async def async_db_session(db_url):
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        
    await engine.dispose()

# 4. Async HTTP Client for FastAPI Endpoints
@pytest_asyncio.fixture
async def api_client(db_url):
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_async_db():
        from app.core.tenant import get_current_tenant
        tenant_id = get_current_tenant()
        async with async_session() as session:
            if tenant_id:
                safe_schema = "".join(c for c in tenant_id if c.isalnum() or c == "_")
                await session.execute(text(f'SET search_path TO "{safe_schema}", public'))
            yield session

    # Override the app dependency with the test container database
    app.dependency_overrides[get_async_db] = _override_get_async_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    app.dependency_overrides.clear()
    await engine.dispose()
