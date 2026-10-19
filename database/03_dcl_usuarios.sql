-- ============================================================
-- PROYECTO FORMATIVO: API REST GASTRONOMIA - SENA CGDSS
-- FICHA: 3312744
-- INSTRUCTIVO: EA4
-- SCRIPT: 03_dcl_usuarios.sql
-- MOTOR: MySQL 8.0
-- DESCRIPCIÓN: Creación de usuario de aplicación con privilegios mínimos (Principio de Menor Privilegio)
-- ============================================================

USE bd_gastronomia;

-- Crear usuario para la aplicación si no existe
CREATE USER IF NOT EXISTS 'usr_gastronomia'@'%' IDENTIFIED BY 'GastronomiaPass2026*';

-- Asignar estrictamente privilegios DML sobre la base de datos del proyecto
-- Se excluyen privilegios administrativos como DROP, ALTER, CREATE USER, GRANT OPTION
GRANT SELECT, INSERT, UPDATE, DELETE ON bd_gastronomia.* TO 'usr_gastronomia'@'%';

-- Aplicar los cambios de privilegios de inmediato
FLUSH PRIVILEGES;

-- Evidencia de permisos otorgados
SHOW GRANTS FOR 'usr_gastronomia'@'%';
