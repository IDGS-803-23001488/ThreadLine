-- =============================================================
-- SEED DATA — ThreadLine
-- Ejecutar DESPUÉS de que Flask haya creado las tablas
-- (python app.py crea tablas y seed básico de admin/permisos)
-- =============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET NAMES utf8mb4;

-- =============================================================
-- COLORES
-- =============================================================
INSERT IGNORE INTO color (id, nombre, hex, activo, fecha_creacion) VALUES
(1,  'Negro',          '#1a1a1a', 1, NOW()),
(2,  'Blanco',         '#ffffff', 1, NOW()),
(3,  'Gris',           '#6b7280', 1, NOW()),
(4,  'Azul marino',    '#1e3a5f', 1, NOW()),
(5,  'Rojo',           '#dc2626', 1, NOW()),
(6,  'Verde olivo',    '#4a5c2e', 1, NOW()),
(7,  'Beige',          '#d4b896', 1, NOW()),
(8,  'Azul cielo',     '#7ec8e3', 1, NOW()),
(9,  'Rosa palo',      '#f4a7b9', 1, NOW()),
(10, 'Café',           '#6f4e37', 1, NOW());

-- =============================================================
-- TALLAS
-- =============================================================
INSERT IGNORE INTO talla (id, nombre, orden, activo, fecha_creacion) VALUES
(1, 'XS',  1, 1, NOW()),
(2, 'S',   2, 1, NOW()),
(3, 'M',   3, 1, NOW()),
(4, 'L',   4, 1, NOW()),
(5, 'XL',  5, 1, NOW()),
(6, 'XXL', 6, 1, NOW()),
(7, '28',  7, 1, NOW()),
(8, '30',  8, 1, NOW()),
(9, '32',  9, 1, NOW()),
(10,'34', 10, 1, NOW()),
(11,'36', 11, 1, NOW());

-- =============================================================
-- UNIDADES
-- =============================================================
INSERT IGNORE INTO unidad (id, unidad, sigla, cantidad, activo, fecha_creacion) VALUES
(1, 'Metro',       'm',   1,    1, NOW()),
(2, 'Kilogramo',   'kg',  1,    1, NOW()),
(3, 'Gramo',       'g',   1000, 1, NOW()),
(4, 'Pieza',       'pza', 1,    1, NOW()),
(5, 'Rollo',       'rol', 1,    1, NOW()),
(6, 'Litro',       'lt',  1,    1, NOW()),
(7, 'Mililitro',   'ml',  1000, 1, NOW()),
(8, 'Yarda',       'yd',  1,    1, NOW()),
(9, 'Par',         'par', 1,    1, NOW()),
(10,'Docena',      'doc', 12,   1, NOW());

-- =============================================================
-- EMPAQUES
-- =============================================================
INSERT IGNORE INTO empaque (id, paquete, unidad_id, cantidad, activo, fecha_creacion) VALUES
(1, 'Rollo de tela (50m)',    1, 50,   1, NOW()),
(2, 'Rollo de tela (100m)',   1, 100,  1, NOW()),
(3, 'Paquete de botones',     4, 144,  1, NOW()),
(4, 'Carrete de hilo',        4, 1,    1, NOW()),
(5, 'Rollo de cierres',       4, 50,   1, NOW()),
(6, 'Bolsa de etiquetas',     4, 500,  1, NOW()),
(7, 'Caja de agujas',         4, 100,  1, NOW()),
(8, 'Galón de tinte',         6, 4,    1, NOW()),
(9, 'Rollo de elástico (50m)',1, 50,   1, NOW()),
(10,'Paquete de remaches',    4, 200,  1, NOW());

-- =============================================================
-- CATEGORÍAS
-- =============================================================
INSERT IGNORE INTO categoria (id, nombre, descripcion, activo, fecha_creacion) VALUES
(1, 'Camisetas',     'Playeras y camisetas de manga corta y larga',  1, NOW()),
(2, 'Pantalones',    'Pantalones de mezclilla, gabardina y casual',  1, NOW()),
(3, 'Shorts',        'Shorts y bermudas para caballero y dama',      1, NOW()),
(4, 'Vestidos',      'Vestidos casuales y de noche',                 1, NOW()),
(5, 'Chamarras',     'Chamarras y chaquetas ligeras',                1, NOW()),
(6, 'Sudaderas',     'Sudaderas con y sin capucha',                  1, NOW()),
(7, 'Blusas',        'Blusas para dama',                             1, NOW()),
(8, 'Ropa interior', 'Ropa interior para caballero y dama',          1, NOW()),
(9, 'Accesorios',    'Cinturones, gorras y complementos',            1, NOW()),
(10,'Deportiva',     'Ropa para actividad física y deporte',         1, NOW());

-- =============================================================
-- PROVEEDORES
-- =============================================================
INSERT IGNORE INTO proveedor (id, nombre, rfc, correo, activo, fecha_creacion) VALUES
(1, 'Textiles del Centro SA de CV',  'TEC010101AAA', 'ventas@textilescentro.mx',   1, NOW()),
(2, 'Hilos y Botones León',          'HBL020202BBB', 'contacto@hilosbotones.mx',   1, NOW()),
(3, 'Importadora Tela Plus',         'ITP030303CCC', 'pedidos@telaplus.com.mx',    1, NOW()),
(4, 'Distribuidora Confección MX',   'DCM040404DDD', 'compras@confeccionmx.mx',    1, NOW()),
(5, 'Accesorios Moda Industrial',    'AMI050505EEE', 'info@modaindustrial.mx',     1, NOW()),
(6, 'Telas Naturales del Bajío',     'TNB060606FFF', 'naturales@telabajio.mx',     1, NOW()),
(7, 'Sintéticos de México',          'SDM070707GGG', 'ventas@sinteticos.mx',       1, NOW()),
(8, 'Cremalleras y Cierres SA',      'CCS080808HHH', 'cierres@cremalleras.mx',     1, NOW());

-- =============================================================
-- MATERIAS PRIMAS  (articulo_id se deja NULL — manejo propio)
-- =============================================================
INSERT IGNORE INTO materia_prima
    (id, nombre, unidad_id, empaque_id, proveedor_id,
     stock_minimo, stock_maximo, activo, fecha_creacion)
VALUES
-- Telas
(1,  'Tela jersey algodón 180g',    1,  1, 1,  50.0000, 500.0000, 1, NOW()),
(2,  'Tela mezclilla 12oz',         1,  2, 3,  30.0000, 300.0000, 1, NOW()),
(3,  'Tela gabardina stretch',      1,  1, 1,  20.0000, 200.0000, 1, NOW()),
(4,  'Tela polar fleece',           1,  2, 6,  15.0000, 150.0000, 1, NOW()),
(5,  'Tela licra deportiva',        1,  1, 7,  10.0000, 100.0000, 1, NOW()),
(6,  'Tela lino natural',           1,  1, 6,  10.0000,  80.0000, 1, NOW()),
(7,  'Tela popelina blanca',        1,  2, 1,  20.0000, 200.0000, 1, NOW()),
(8,  'Tela French Terry',           1,  1, 4,  15.0000, 150.0000, 1, NOW()),
(9,  'Tela oxford 600D',            1,  2, 3,  10.0000,  80.0000, 1, NOW()),
(10, 'Tela seda artificial',        1,  1, 1,   5.0000,  50.0000, 1, NOW()),
-- Hilos
(11, 'Hilo poliéster negro 40/2',   4,  4, 2, 100.0000, 999.0000, 1, NOW()),
(12, 'Hilo algodón blanco 40/2',    4,  4, 2, 100.0000, 999.0000, 1, NOW()),
(13, 'Hilo overlock gris',          4,  4, 2,  50.0000, 500.0000, 1, NOW()),
(14, 'Hilo elástico transparente',  4,  4, 2,  20.0000, 200.0000, 1, NOW()),
-- Avíos
(15, 'Cierre metálico 20cm',        4,  5, 8, 200.0000,1000.0000, 1, NOW()),
(16, 'Cierre de plástico 15cm',     4,  5, 8, 200.0000,1000.0000, 1, NOW()),
(17, 'Botón camisa 4 hoyos 12mm',   4,  3, 2, 500.0000,5000.0000, 1, NOW()),
(18, 'Botón pantalón metálico',     4,  3, 5, 200.0000,2000.0000, 1, NOW()),
(19, 'Elástico de 3cm',             1,  9, 4,  20.0000, 200.0000, 1, NOW()),
(20, 'Etiqueta tejida marca',       4,  6, 4, 500.0000,5000.0000, 1, NOW()),
(21, 'Etiqueta talla y lavado',     4,  6, 4, 500.0000,5000.0000, 1, NOW()),
(22, 'Remache metálico dorado',     4, 10, 5, 300.0000,3000.0000, 1, NOW()),
(23, 'Hombrera espuma 1cm',         9,  4, 4,  20.0000, 200.0000, 1, NOW()),
(24, 'Cordón capucha redondo 1cm',  1,  4, 4,  10.0000, 100.0000, 1, NOW()),
(25, 'Entretela termoadherible',    1,  1, 1,  10.0000, 100.0000, 1, NOW());

-- =============================================================
-- PRODUCTOS
-- =============================================================
INSERT IGNORE INTO producto
    (id, nombre, categoria_id, descripcion, color_id, activo, fecha_creacion)
VALUES
(1,  'Playera Básica',         1, 'Playera cuello redondo 100% algodón',           1, 1, NOW()),
(2,  'Playera Básica',         1, 'Playera cuello redondo 100% algodón',           2, 1, NOW()),
(3,  'Playera Básica',         1, 'Playera cuello redondo 100% algodón',           3, 1, NOW()),
(4,  'Playera Polo',           1, 'Polo piqué manga corta con cuello',             4, 1, NOW()),
(5,  'Playera Polo',           1, 'Polo piqué manga corta con cuello',             1, 1, NOW()),
(6,  'Pantalón Mezclilla Slim',2, 'Pantalón de mezclilla corte slim',             4, 1, NOW()),
(7,  'Pantalón Mezclilla Slim',2, 'Pantalón de mezclilla corte slim',             1, 1, NOW()),
(8,  'Pantalón Gabardina',     2, 'Pantalón gabardina stretch corte recto',        3, 1, NOW()),
(9,  'Short Deportivo',        3, 'Short con bolsillos y elástico en cintura',     1, 1, NOW()),
(10, 'Short Deportivo',        3, 'Short con bolsillos y elástico en cintura',     5, 1, NOW()),
(11, 'Sudadera con Capucha',   6, 'Hoodie French Terry unisex',                   1, 1, NOW()),
(12, 'Sudadera con Capucha',   6, 'Hoodie French Terry unisex',                   3, 1, NOW()),
(13, 'Sudadera sin Capucha',   6, 'Crewneck French Terry unisex',                 2, 1, NOW()),
(14, 'Chamarra Ligera',        5, 'Chamarra rompevientos con forro',               4, 1, NOW()),
(15, 'Vestido Casual',         4, 'Vestido jersey manga corta midi',               9, 1, NOW()),
(16, 'Blusa Popelina',         7, 'Blusa de popelina con botones frontales',       2, 1, NOW()),
(17, 'Top Deportivo',         10, 'Top licra para actividad física',               5, 1, NOW()),
(18, 'Leggins Deportivos',    10, 'Leggins compresión con bolsillo lateral',       1, 1, NOW()),
(19, 'Pantalón Cargo',         2, 'Pantalón cargo multibolsillos',                 6, 1, NOW()),
(20, 'Camiseta Oversize',      1, 'Camiseta holgada unisex longline',              7, 1, NOW());

-- =============================================================
-- ARTÍCULOS (tipo PRODUCTO, uno por variante se crea abajo)
-- Se crean registros base de artículo para cada producto_variante
-- =============================================================
-- Nota: en tu modelo, articulo_id en producto_variante es opcional.
-- Se insertan los artículos y variantes juntos por simplicidad.

-- Artículos 1-60 para las variantes de producto
INSERT IGNORE INTO articulo (id, tipo, activo, fecha_creacion) VALUES
(1,  'PRODUCTO', 1, NOW()), (2,  'PRODUCTO', 1, NOW()), (3,  'PRODUCTO', 1, NOW()),
(4,  'PRODUCTO', 1, NOW()), (5,  'PRODUCTO', 1, NOW()), (6,  'PRODUCTO', 1, NOW()),
(7,  'PRODUCTO', 1, NOW()), (8,  'PRODUCTO', 1, NOW()), (9,  'PRODUCTO', 1, NOW()),
(10, 'PRODUCTO', 1, NOW()), (11, 'PRODUCTO', 1, NOW()), (12, 'PRODUCTO', 1, NOW()),
(13, 'PRODUCTO', 1, NOW()), (14, 'PRODUCTO', 1, NOW()), (15, 'PRODUCTO', 1, NOW()),
(16, 'PRODUCTO', 1, NOW()), (17, 'PRODUCTO', 1, NOW()), (18, 'PRODUCTO', 1, NOW()),
(19, 'PRODUCTO', 1, NOW()), (20, 'PRODUCTO', 1, NOW()), (21, 'PRODUCTO', 1, NOW()),
(22, 'PRODUCTO', 1, NOW()), (23, 'PRODUCTO', 1, NOW()), (24, 'PRODUCTO', 1, NOW()),
(25, 'PRODUCTO', 1, NOW()), (26, 'PRODUCTO', 1, NOW()), (27, 'PRODUCTO', 1, NOW()),
(28, 'PRODUCTO', 1, NOW()), (29, 'PRODUCTO', 1, NOW()), (30, 'PRODUCTO', 1, NOW()),
(31, 'PRODUCTO', 1, NOW()), (32, 'PRODUCTO', 1, NOW()), (33, 'PRODUCTO', 1, NOW()),
(34, 'PRODUCTO', 1, NOW()), (35, 'PRODUCTO', 1, NOW()), (36, 'PRODUCTO', 1, NOW()),
(37, 'PRODUCTO', 1, NOW()), (38, 'PRODUCTO', 1, NOW()), (39, 'PRODUCTO', 1, NOW()),
(40, 'PRODUCTO', 1, NOW()), (41, 'PRODUCTO', 1, NOW()), (42, 'PRODUCTO', 1, NOW()),
(43, 'PRODUCTO', 1, NOW()), (44, 'PRODUCTO', 1, NOW()), (45, 'PRODUCTO', 1, NOW()),
(46, 'PRODUCTO', 1, NOW()), (47, 'PRODUCTO', 1, NOW()), (48, 'PRODUCTO', 1, NOW()),
(49, 'PRODUCTO', 1, NOW()), (50, 'PRODUCTO', 1, NOW()), (51, 'PRODUCTO', 1, NOW()),
(52, 'PRODUCTO', 1, NOW()), (53, 'PRODUCTO', 1, NOW()), (54, 'PRODUCTO', 1, NOW()),
(55, 'PRODUCTO', 1, NOW()), (56, 'PRODUCTO', 1, NOW()), (57, 'PRODUCTO', 1, NOW()),
(58, 'PRODUCTO', 1, NOW()), (59, 'PRODUCTO', 1, NOW()), (60, 'PRODUCTO', 1, NOW()),
-- Artículos para materias primas
(101,'MATERIA_PRIMA', 1, NOW()), (102,'MATERIA_PRIMA', 1, NOW()),
(103,'MATERIA_PRIMA', 1, NOW()), (104,'MATERIA_PRIMA', 1, NOW()),
(105,'MATERIA_PRIMA', 1, NOW());

-- =============================================================
-- PRODUCTO_VARIANTE
-- producto_id × talla_id  (tallas relevantes por tipo de prenda)
-- =============================================================
INSERT IGNORE INTO producto_variante
    (id, articulo_id, producto_id, talla_id, precio_venta, activo, fecha_creacion)
VALUES
-- Playera Básica Negra (prod 1) — tallas XS-XXL
(1,  1,  1, 1, 189.00, 1, NOW()),
(2,  2,  1, 2, 189.00, 1, NOW()),
(3,  3,  1, 3, 189.00, 1, NOW()),
(4,  4,  1, 4, 189.00, 1, NOW()),
(5,  5,  1, 5, 199.00, 1, NOW()),
(6,  6,  1, 6, 209.00, 1, NOW()),
-- Playera Básica Blanca (prod 2)
(7,  7,  2, 2, 189.00, 1, NOW()),
(8,  8,  2, 3, 189.00, 1, NOW()),
(9,  9,  2, 4, 189.00, 1, NOW()),
(10, 10, 2, 5, 199.00, 1, NOW()),
-- Playera Básica Gris (prod 3)
(11, 11, 3, 2, 189.00, 1, NOW()),
(12, 12, 3, 3, 189.00, 1, NOW()),
(13, 13, 3, 4, 189.00, 1, NOW()),
-- Playera Polo Marino (prod 4)
(14, 14, 4, 2, 349.00, 1, NOW()),
(15, 15, 4, 3, 349.00, 1, NOW()),
(16, 16, 4, 4, 349.00, 1, NOW()),
(17, 17, 4, 5, 369.00, 1, NOW()),
-- Playera Polo Negro (prod 5)
(18, 18, 5, 2, 349.00, 1, NOW()),
(19, 19, 5, 3, 349.00, 1, NOW()),
(20, 20, 5, 4, 349.00, 1, NOW()),
-- Pantalón Mezclilla Slim Marino (prod 6) — tallas numéricas
(21, 21, 6, 7,  599.00, 1, NOW()),
(22, 22, 6, 8,  599.00, 1, NOW()),
(23, 23, 6, 9,  599.00, 1, NOW()),
(24, 24, 6, 10, 599.00, 1, NOW()),
(25, 25, 6, 11, 619.00, 1, NOW()),
-- Pantalón Mezclilla Slim Negro (prod 7)
(26, 26, 7, 8,  599.00, 1, NOW()),
(27, 27, 7, 9,  599.00, 1, NOW()),
(28, 28, 7, 10, 599.00, 1, NOW()),
-- Pantalón Gabardina Gris (prod 8)
(29, 29, 8, 7,  549.00, 1, NOW()),
(30, 30, 8, 8,  549.00, 1, NOW()),
(31, 31, 8, 9,  549.00, 1, NOW()),
(32, 32, 8, 10, 549.00, 1, NOW()),
-- Short Deportivo Negro (prod 9)
(33, 33, 9, 2, 249.00, 1, NOW()),
(34, 34, 9, 3, 249.00, 1, NOW()),
(35, 35, 9, 4, 249.00, 1, NOW()),
(36, 36, 9, 5, 259.00, 1, NOW()),
-- Short Deportivo Rojo (prod 10)
(37, 37, 10, 3, 249.00, 1, NOW()),
(38, 38, 10, 4, 249.00, 1, NOW()),
-- Sudadera Capucha Negra (prod 11)
(39, 39, 11, 2, 599.00, 1, NOW()),
(40, 40, 11, 3, 599.00, 1, NOW()),
(41, 41, 11, 4, 599.00, 1, NOW()),
(42, 42, 11, 5, 629.00, 1, NOW()),
-- Sudadera Capucha Gris (prod 12)
(43, 43, 12, 3, 599.00, 1, NOW()),
(44, 44, 12, 4, 599.00, 1, NOW()),
-- Sudadera sin Capucha Blanca (prod 13)
(45, 45, 13, 2, 549.00, 1, NOW()),
(46, 46, 13, 3, 549.00, 1, NOW()),
(47, 47, 13, 4, 549.00, 1, NOW()),
-- Chamarra Ligera Marina (prod 14)
(48, 48, 14, 2, 799.00, 1, NOW()),
(49, 49, 14, 3, 799.00, 1, NOW()),
(50, 50, 14, 4, 799.00, 1, NOW()),
-- Vestido Casual Rosa (prod 15)
(51, 51, 15, 1, 499.00, 1, NOW()),
(52, 52, 15, 2, 499.00, 1, NOW()),
(53, 53, 15, 3, 499.00, 1, NOW()),
-- Blusa Popelina Blanca (prod 16)
(54, 54, 16, 1, 379.00, 1, NOW()),
(55, 55, 16, 2, 379.00, 1, NOW()),
(56, 56, 16, 3, 379.00, 1, NOW()),
-- Top Deportivo (prod 17)
(57, 57, 17, 1, 229.00, 1, NOW()),
(58, 58, 17, 2, 229.00, 1, NOW()),
(59, 59, 17, 3, 229.00, 1, NOW()),
-- Leggins (prod 18)
(60, 60, 18, 2, 329.00, 1, NOW());

-- =============================================================
-- INVENTARIOS
-- =============================================================
INSERT IGNORE INTO inventarios (id, nombre, tipo, activo, fecha_creacion) VALUES
(1, 'Almacén Principal',       0, 1, NOW()),
(2, 'Almacén Materia Prima',   0, 1, NOW()),
(3, 'Almacén Producto Terminado', 1, 1, NOW()),
(4, 'Almacén Mermas',          0, 1, NOW());

-- =============================================================
-- TIPOS DE MOVIMIENTO
-- =============================================================
INSERT IGNORE INTO tipo_movimientos (id, tipo, signo, activo, fecha_creacion) VALUES
(1, 'Compra',             1,  1, NOW()),
(2, 'Venta',             -1,  1, NOW()),
(3, 'Ajuste positivo',    1,  1, NOW()),
(4, 'Ajuste negativo',   -1,  1, NOW()),
(5, 'Entrada producción', 1,  1, NOW()),
(6, 'Salida producción', -1,  1, NOW()),
(7, 'Merma',             -1,  1, NOW()),
(8, 'Devolución compra', -1,  1, NOW()),
(9, 'Devolución venta',   1,  1, NOW());

-- =============================================================
-- CLIENTES
-- =============================================================
INSERT IGNORE INTO cliente
    (id, nombre, correo, contrasenia, telefono, direccion, activo, fecha_creacion)
VALUES
(1,  'María López',       'maria.lopez@gmail.com',     '$2b$12$dummy_hash_1', '4771234567', 'Blvd. López Mateos 100, León, Gto.',    1, NOW()),
(2,  'Carlos Ramírez',    'c.ramirez@hotmail.com',     '$2b$12$dummy_hash_2', '4779876543', 'Av. Insurgentes 250, León, Gto.',        1, NOW()),
(3,  'Ana Martínez',      'ana.mtz@outlook.com',       '$2b$12$dummy_hash_3', '4772345678', 'Calle Hermanos Aldama 45, León, Gto.',   1, NOW()),
(4,  'Jorge Hernández',   'jorge.hdz@gmail.com',       '$2b$12$dummy_hash_4', '4773456789', 'Paseo de los Insurgentes 88, León, Gto.',1, NOW()),
(5,  'Laura Sánchez',     'lsanchez@yahoo.com.mx',     '$2b$12$dummy_hash_5', '4774567890', 'Blvd. Aeropuerto 320, León, Gto.',       1, NOW()),
(6,  'Roberto García',    'r.garcia@empresa.com',      '$2b$12$dummy_hash_6', '4775678901', 'Av. Tecnológico 500, León, Gto.',        1, NOW()),
(7,  'Sofía Torres',      'sofia.torres@gmail.com',    '$2b$12$dummy_hash_7', '4776789012', 'Calle Pedro Moreno 12, Silao, Gto.',     1, NOW()),
(8,  'Diego Flores',      'dflores@mail.com',          '$2b$12$dummy_hash_8', '4777890123', 'Blvd. Timoteo Lozano 77, León, Gto.',    1, NOW()),
(9,  'Valentina Cruz',    'vcruz@correo.mx',           '$2b$12$dummy_hash_9', '4778901234', 'Av. Juárez 1200, Irapuato, Gto.',        1, NOW()),
(10, 'Miguel Ángel Ruiz', 'maruiz@gmail.com',          '$2b$12$dummy_hash_0', '4770123456', 'Calle Madero 300, Salamanca, Gto.',      1, NOW());

-- =============================================================
-- RECETAS
-- (solo para playera básica y sudadera como ejemplos completos)
-- =============================================================
INSERT IGNORE INTO receta
    (id, producto_variante_id, cantidad_base, activo, fecha_creacion)
VALUES
(1, 3,  1, 1, NOW()),   -- Playera Básica Negra M
(2, 8,  1, 1, NOW()),   -- Playera Básica Blanca M
(3, 40, 1, 1, NOW()),   -- Sudadera Capucha Negra M
(4, 34, 1, 1, NOW());   -- Short Deportivo Negro M

-- Detalles receta Playera Básica (1.6m tela + hilos + etiquetas)
INSERT IGNORE INTO receta_detalle
    (id, receta_id, materia_prima_id, cantidad_neta)
VALUES
(1,  1, 1,  1.6000),   -- Tela jersey algodón 1.6m
(2,  1, 11, 2.0000),   -- Hilo poliéster negro (carretes)
(3,  1, 13, 1.0000),   -- Hilo overlock
(4,  1, 20, 1.0000),   -- Etiqueta marca
(5,  1, 21, 1.0000),   -- Etiqueta talla/lavado

-- Detalles receta Playera Básica Blanca
(6,  2, 1,  1.6000),
(7,  2, 12, 2.0000),   -- Hilo blanco
(8,  2, 13, 1.0000),
(9,  2, 20, 1.0000),
(10, 2, 21, 1.0000),

-- Detalles receta Sudadera con Capucha Negra (más insumos)
(11, 3, 8,  2.2000),   -- French Terry 2.2m
(12, 3, 11, 3.0000),   -- Hilo negro
(13, 3, 13, 2.0000),   -- Hilo overlock
(14, 3, 19, 0.3000),   -- Elástico 30cm cintura/puños
(15, 3, 24, 1.5000),   -- Cordón capucha 1.5m
(16, 3, 20, 1.0000),   -- Etiqueta marca
(17, 3, 21, 1.0000),   -- Etiqueta talla

-- Detalles receta Short Deportivo
(18, 4, 5,  0.8000),   -- Tela licra deportiva
(19, 4, 11, 1.0000),   -- Hilo negro
(20, 4, 13, 1.0000),   -- Overlock
(21, 4, 19, 0.2500),   -- Elástico cintura
(22, 4, 20, 1.0000),
(23, 4, 21, 1.0000);

-- =============================================================
-- PEDIDOS de prueba
-- =============================================================
INSERT IGNORE INTO pedido
    (id, cliente_id, folio, fecha, subtotal, costo_envio, total,
     estatus, direccion_envio)
VALUES
(1, 1, 'PED-2025-0001', DATE_SUB(NOW(), INTERVAL 30 DAY), 567.00, 99.00,  666.00, 'entregado',  'Blvd. López Mateos 100, León, Gto.'),
(2, 2, 'PED-2025-0002', DATE_SUB(NOW(), INTERVAL 25 DAY), 349.00, 0.00,   349.00, 'entregado',  'Av. Insurgentes 250, León, Gto.'),
(3, 3, 'PED-2025-0003', DATE_SUB(NOW(), INTERVAL 18 DAY), 948.00, 99.00, 1047.00, 'entregado',  'Calle Hermanos Aldama 45, León, Gto.'),
(4, 4, 'PED-2025-0004', DATE_SUB(NOW(), INTERVAL 12 DAY), 599.00, 0.00,   599.00, 'enviado',    'Paseo de los Insurgentes 88, León, Gto.'),
(5, 5, 'PED-2025-0005', DATE_SUB(NOW(), INTERVAL 8 DAY),  798.00, 99.00,  897.00, 'enviado',    'Blvd. Aeropuerto 320, León, Gto.'),
(6, 1, 'PED-2025-0006', DATE_SUB(NOW(), INTERVAL 5 DAY),  599.00, 0.00,   599.00, 'procesando', 'Blvd. López Mateos 100, León, Gto.'),
(7, 6, 'PED-2025-0007', DATE_SUB(NOW(), INTERVAL 3 DAY), 1148.00, 99.00, 1247.00, 'procesando', 'Av. Tecnológico 500, León, Gto.'),
(8, 7, 'PED-2025-0008', DATE_SUB(NOW(), INTERVAL 1 DAY),  379.00, 99.00,  478.00, 'pendiente',  'Calle Pedro Moreno 12, Silao, Gto.'),
(9, 8, 'PED-2025-0009', NOW(),                            1199.00, 0.00,  1199.00, 'pendiente',  'Blvd. Timoteo Lozano 77, León, Gto.'),
(10,9, 'PED-2025-0010', NOW(),                             499.00, 99.00,  598.00, 'pendiente',  'Av. Juárez 1200, Irapuato, Gto.');

-- =============================================================
-- PEDIDO DETALLES
-- =============================================================
INSERT IGNORE INTO pedido_detalle
    (id, pedido_id, producto_variante_id, cantidad, precio_unitario, subtotal)
VALUES
(1,  1, 3,  2, 189.00, 378.00),
(2,  1, 34, 1, 189.00, 189.00),
(3,  2, 15, 1, 349.00, 349.00),
(4,  3, 40, 1, 599.00, 599.00),
(5,  3, 3,  1, 189.00, 189.00),
(6,  3, 34, 1, 249.00, 249.00),  -- corregido: short 249
(7,  4, 22, 1, 599.00, 599.00),
(8,  5, 43, 1, 599.00, 599.00),
(9,  5, 11, 1, 199.00, 199.00),
(10, 6, 24, 1, 599.00, 599.00),
(11, 7, 39, 1, 599.00, 599.00),
(12, 7, 48, 1, 549.00, 549.00),
(13, 8, 54, 1, 379.00, 379.00),
(14, 9, 41, 1, 599.00, 599.00),
(15, 9, 42, 1, 629.00, 629.00),  -- XXL
(16,10, 51, 1, 499.00, 499.00);

-- =============================================================
-- PAGOS
-- =============================================================
INSERT IGNORE INTO pago
    (id, pedido_id, metodo, referencia, monto, estatus, fecha)
VALUES
(1,  1, 'tarjeta',      'TXN-4A2F91',   666.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 30 DAY)),
(2,  2, 'transferencia','REF-882341',    349.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 25 DAY)),
(3,  3, 'tarjeta',      'TXN-7B3C44',  1047.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 18 DAY)),
(4,  4, 'tarjeta',      'TXN-9D1E22',   599.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 12 DAY)),
(5,  5, 'oxxo',         'OXXO-55512',   897.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 8 DAY)),
(6,  6, 'transferencia','REF-991022',   599.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 5 DAY)),
(7,  7, 'tarjeta',      'TXN-1F8A77',  1247.00, 'pendiente', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(8,  8, 'simulado',     NULL,            478.00, 'pendiente', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(9,  9, 'simulado',     NULL,           1199.00, 'pendiente', NOW()),
(10,10, 'oxxo',         'OXXO-88832',   598.00, 'pendiente', NOW());

-- =============================================================
-- RESEÑAS
-- =============================================================
INSERT IGNORE INTO resenia
    (id, cliente_id, producto_id, calificacion, comentario, verificada, fecha)
VALUES
(1,  1,  1, 5, 'Excelente calidad, el algodón es muy suave y la talla M me quedó perfecto.',             1, DATE_SUB(NOW(), INTERVAL 28 DAY)),
(2,  2,  4, 4, 'Muy buen polo, se ve elegante. Le doy 4 porque tardó un poco en llegar.',                1, DATE_SUB(NOW(), INTERVAL 22 DAY)),
(3,  3, 11, 5, 'La sudadera es increíble, muy abrigadora y el material no se destiñe.',                  1, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(4,  4,  6, 4, 'Buen pantalón, cae muy bien. El azul marino es idéntico a las fotos.',                   1, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(5,  5, 12, 3, 'La calidad es buena pero el gris me llegó un poco más oscuro de lo esperado.',           1, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(6,  6, 11, 5, 'Segunda compra de esta sudadera, sin duda la mejor que he tenido.',                      0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(7,  7, 16, 5, 'La blusa es preciosa, perfecta para la oficina. El popelín es de buena calidad.',        0, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(8,  1,  9, 4, 'El short es muy cómodo para hacer ejercicio, el elástico no aprieta.',                   1, DATE_SUB(NOW(), INTERVAL 25 DAY));

-- =============================================================
-- COMPRAS DE MATERIA PRIMA
-- =============================================================
INSERT IGNORE INTO compra
    (id, proveedor_id, fecha, total, estatus, observaciones, fecha_creacion)
VALUES
(1, 1, DATE_SUB(NOW(), INTERVAL 45 DAY), 12500.00, 'recibido',  'Pedido quincenal de tela jersey',          NOW()),
(2, 2, DATE_SUB(NOW(), INTERVAL 40 DAY),  3200.00, 'recibido',  'Reposición de hilos y avíos',              NOW()),
(3, 3, DATE_SUB(NOW(), INTERVAL 30 DAY), 18000.00, 'recibido',  'Compra de tela mezclilla importada',       NOW()),
(4, 2, DATE_SUB(NOW(), INTERVAL 20 DAY),  1800.00, 'recibido',  'Botones, etiquetas y cierres',             NOW()),
(5, 6, DATE_SUB(NOW(), INTERVAL 15 DAY),  9500.00, 'recibido',  'Telas naturales: lino y popelina',         NOW()),
(6, 4, DATE_SUB(NOW(), INTERVAL 10 DAY),  6200.00, 'en_transito','French Terry y Polar Fleece',             NOW()),
(7, 1, DATE_SUB(NOW(), INTERVAL  5 DAY),  8400.00, 'pendiente', 'Tela jersey para siguiente temporada',     NOW());

-- COMPRA DETALLES
INSERT IGNORE INTO compra_detalle
    (id, compra_id, materia_prima_id,
     cantidad_empaque, cantidad_unidad, precio_unitario, subtotal)
VALUES
-- Compra 1: Tela jersey algodón
(1,  1, 1,  2.0000, 100.0000, 125.00, 12500.00),
-- Compra 2: Hilos y avíos
(2,  2, 11, 10.0000, 10.0000, 180.00,  1800.00),
(3,  2, 12, 10.0000, 10.0000, 180.00,  1800.00),
-- Compra 3: Mezclilla
(4,  3, 2,  3.0000, 300.0000,  60.00, 18000.00),
-- Compra 4: Botones y avíos
(5,  4, 17, 2.0000, 288.0000,   4.50,  1296.00),
(6,  4, 20, 1.0000, 500.0000,   1.00,   500.00),
(7,  4, 21, 1.0000, 500.0000,   0.50,   250.00),
-- Compra 5: Telas naturales
(8,  5, 6,  1.0000,  50.0000,  90.00,  4500.00),
(9,  5, 7,  2.0000, 100.0000,  50.00,  5000.00),
-- Compra 6: French Terry
(10, 6, 8,  2.0000, 100.0000,  62.00,  6200.00),
-- Compra 7: Tela jersey (pedido abierto)
(11, 7, 1,  2.0000, 100.0000,  84.00,  8400.00);

-- =============================================================
-- ÓRDENES DE PRODUCCIÓN (algunas completadas, otras en progreso)
-- =============================================================
INSERT IGNORE INTO orden_produccion
    (id, receta_id, cantidad_solicitada, cantidad_producida,
     estatus, fecha_inicio, fecha_fin)
VALUES
(1, 1, 50, 50, 'completada', DATE_SUB(NOW(), INTERVAL 35 DAY), DATE_SUB(NOW(), INTERVAL 32 DAY)),
(2, 2, 30, 30, 'completada', DATE_SUB(NOW(), INTERVAL 28 DAY), DATE_SUB(NOW(), INTERVAL 26 DAY)),
(3, 3, 20, 20, 'completada', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),
(4, 1, 40, 25, 'en_proceso', DATE_SUB(NOW(), INTERVAL  5 DAY), NULL),
(5, 4, 60,  0, 'pendiente',  NULL, NULL);

-- =============================================================
-- SOLICITUDES DE PRODUCCIÓN
-- =============================================================
INSERT IGNORE INTO solicitud_produccion
    (id, producto_variante_id, cantidad, estatus, observaciones,
     fecha_creacion, solicitado_por, atendido_por)
VALUES
(1, 3,  50, 'atendida',  'Reposición urgente de talla M negro.',     DATE_SUB(NOW(), INTERVAL 36 DAY), 1, 1),
(2, 8,  30, 'atendida',  'Stock bajo en blanca talla M.',            DATE_SUB(NOW(), INTERVAL 29 DAY), 1, 1),
(3, 40, 20, 'atendida',  'Pedido masivo de sudaderas.',               DATE_SUB(NOW(), INTERVAL 21 DAY), 1, 1),
(4, 3,  40, 'en_proceso','Segunda corrida playera negra M.',         DATE_SUB(NOW(), INTERVAL  6 DAY), 1, 1),
(5, 34, 60, 'pendiente', 'Preparar para temporada primavera-verano.',DATE_SUB(NOW(), INTERVAL  1 DAY), 1, NULL);

-- =============================================================
SET FOREIGN_KEY_CHECKS = 1;
-- FIN DEL SEED
-- =============================================================