-- =========================================
-- USERS
-- =========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- ROLES
-- =========================================
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Beispielwerte:
-- SYSTEM_ADMIN
-- FAMILY_ADMIN
-- USER


-- =========================================
-- FAMILIES
-- =========================================
CREATE TABLE families (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- USER ↔ FAMILY ↔ ROLE (RBAC)
-- =========================================
CREATE TABLE user_family_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id INTEGER NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE (user_id, family_id)
);


-- =========================================
-- WIDGET TYPES (Definitionsebene)
-- =========================================
CREATE TABLE widget_types (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,          -- z.B. "todo", "weather", "calendar"
    display_name VARCHAR(255) NOT NULL,
    description TEXT
);


-- =========================================
-- WIDGET INSTANZEN PRO FAMILIE
-- =========================================
CREATE TABLE family_widgets (
    id SERIAL PRIMARY KEY,
    family_id INTEGER NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    widget_type_id INTEGER NOT NULL REFERENCES widget_types(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT TRUE,

    UNIQUE (family_id, widget_type_id)
);


-- =========================================
-- WIDGET-ROLLEN-BERECHTIGUNGEN
-- =========================================
CREATE TABLE widget_role_permissions (
    id SERIAL PRIMARY KEY,
    family_widget_id INTEGER NOT NULL REFERENCES family_widgets(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,

    can_view BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,

    UNIQUE (family_widget_id, role_id)
);


-- =========================================
-- TODOS (eine Liste pro Familie)
-- =========================================
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    family_id INTEGER NOT NULL REFERENCES families(id) ON DELETE CASCADE,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    is_completed BOOLEAN DEFAULT FALSE,
);

