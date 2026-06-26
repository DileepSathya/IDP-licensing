CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    f_name VARCHAR(100) NOT NULL,
    l_name VARCHAR(100) NOT NULL,

    user_type VARCHAR(20) NOT NULL
        CHECK (LOWER(user_type) IN ('individual', 'enterprise')),

    email CITEXT NOT NULL,

    CONSTRAINT users_email_unique UNIQUE (email),

    CONSTRAINT users_email_check
        CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),

    password_hash VARCHAR(255) NOT NULL,

	role VARCHAR(100)
);

