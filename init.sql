CREATE USER persona_user WITH PASSWORD '!default_Bot_password';
CREATE DATABASE persona_bot_db;
GRANT ALL PRIVILEGES ON DATABASE persona_bot_db TO persona_user;

\c persona_bot_db

ALTER SCHEMA public OWNER TO persona_user;
GRANT ALL ON SCHEMA public TO persona_user;

CREATE EXTENSION IF NOT EXISTS vector;