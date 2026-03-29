-- =============================================================
-- SEED DATA — ThreadLine
-- Ejecutar DESPUÉS de que Flask haya creado las tablas
-- y corrido el seed base (admin, roles, permisos)
-- =============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET NAMES utf8mb4;

-- =============================================================
-- COLORES
-- =============================================================
INSERT IGNORE INTO color (id, nombre, hex, activo, fecha_creacion) VALUES
(1,  'Negro',       '#1a1a1a', 1, NOW()),
(2,  'Blanco',      '#ffffff', 1, NOW()),
(3,  'Gris',        '#6b7280', 1, NOW()),
(4,  'Azul marino', '#1e3a5f', 1, NOW()),
(5,  'Rojo',        '#dc2626', 1, NOW()),
(6,  'Verde olivo', '#4a5c2e', 1, NOW()),
(7,  'Beige',       '#d4b896', 1, NOW()),
(8,  'Azul cielo',  '#7ec8e3', 1, NOW()),
(9,  'Rosa palo',   '#f4a7b9', 1, NOW()),
(10, 'Café',        '#6f4e37', 1, NOW());

-- =============================================================
-- TALLAS
-- =============================================================
INSERT IGNORE INTO talla (id, nombre, orden, activo, fecha_creacion) VALUES
(1,  'XS',  1,  1, NOW()),
(2,  'S',   2,  1, NOW()),
(3,  'M',   3,  1, NOW()),
(4,  'L',   4,  1, NOW()),
(5,  'XL',  5,  1, NOW()),
(6,  'XXL', 6,  1, NOW()),
(7,  '28',  7,  1, NOW()),
(8,  '30',  8,  1, NOW()),
(9,  '32',  9,  1, NOW()),
(10, '34',  10, 1, NOW()),
(11, '36',  11, 1, NOW());

-- =============================================================
-- UNIDADES
-- =============================================================
INSERT IGNORE INTO unidad (id, unidad, sigla, cantidad, activo, fecha_creacion) VALUES
(1,  'Metro',     'm',   1,    1, NOW()),
(2,  'Kilogramo', 'kg',  1,    1, NOW()),
(3,  'Gramo',     'g',   1000, 1, NOW()),
(4,  'Pieza',     'pza', 1,    1, NOW()),
(5,  'Rollo',     'rol', 1,    1, NOW()),
(6,  'Litro',     'lt',  1,    1, NOW()),
(7,  'Mililitro', 'ml',  1000, 1, NOW()),
(8,  'Yarda',     'yd',  1,    1, NOW()),
(9,  'Par',       'par', 1,    1, NOW()),
(10, 'Docena',    'doc', 12,   1, NOW());

-- =============================================================
-- EMPAQUES
-- =============================================================
INSERT IGNORE INTO empaque (id, paquete, unidad_id, cantidad, activo, fecha_creacion) VALUES
(1,  'Rollo de tela (50m)',     1, 50,  1, NOW()),
(2,  'Rollo de tela (100m)',    1, 100, 1, NOW()),
(3,  'Paquete de botones',      4, 144, 1, NOW()),
(4,  'Carrete de hilo',         4, 1,   1, NOW()),
(5,  'Rollo de cierres',        4, 50,  1, NOW()),
(6,  'Bolsa de etiquetas',      4, 500, 1, NOW()),
(7,  'Caja de agujas',          4, 100, 1, NOW()),
(8,  'Galón de tinte',          6, 4,   1, NOW()),
(9,  'Rollo de elástico (50m)', 1, 50,  1, NOW()),
(10, 'Paquete de remaches',     4, 200, 1, NOW());

-- =============================================================
-- CATEGORÍAS
-- =============================================================
INSERT IGNORE INTO categoria (id, nombre, descripcion, activo, fecha_creacion) VALUES
(1,  'Camisetas',     'Playeras y camisetas de manga corta y larga', 1, NOW()),
(2,  'Pantalones',    'Pantalones de mezclilla, gabardina y casual', 1, NOW()),
(3,  'Shorts',        'Shorts y bermudas para caballero y dama',     1, NOW()),
(4,  'Vestidos',      'Vestidos casuales y de noche',                1, NOW()),
(5,  'Chamarras',     'Chamarras y chaquetas ligeras',               1, NOW()),
(6,  'Sudaderas',     'Sudaderas con y sin capucha',                 1, NOW()),
(7,  'Blusas',        'Blusas para dama',                            1, NOW()),
(8,  'Ropa interior', 'Ropa interior para caballero y dama',         1, NOW()),
(9,  'Accesorios',    'Cinturones, gorras y complementos',           1, NOW()),
(10, 'Deportiva',     'Ropa para actividad física y deporte',        1, NOW());

-- =============================================================
-- PROVEEDORES
-- =============================================================
INSERT IGNORE INTO proveedor (id, nombre, rfc, correo, activo, fecha_creacion) VALUES
(1, 'Textiles del Centro SA de CV', 'TEC010101AAA', 'ventas@textilescentro.mx',  1, NOW()),
(2, 'Hilos y Botones León',         'HBL020202BBB', 'contacto@hilosbotones.mx',  1, NOW()),
(3, 'Importadora Tela Plus',        'ITP030303CCC', 'pedidos@telaplus.com.mx',   1, NOW()),
(4, 'Distribuidora Confección MX',  'DCM040404DDD', 'compras@confeccionmx.mx',   1, NOW()),
(5, 'Accesorios Moda Industrial',   'AMI050505EEE', 'info@modaindustrial.mx',    1, NOW()),
(6, 'Telas Naturales del Bajío',    'TNB060606FFF', 'naturales@telabajio.mx',    1, NOW()),
(7, 'Sintéticos de México',         'SDM070707GGG', 'ventas@sinteticos.mx',      1, NOW()),
(8, 'Cremalleras y Cierres SA',     'CCS080808HHH', 'cierres@cremalleras.mx',    1, NOW());

-- =============================================================
-- MATERIAS PRIMAS
-- NOTA: porcentaje_merma está comentado en el modelo, se omite
-- =============================================================
INSERT IGNORE INTO materia_prima
    (id, nombre, unidad_id, empaque_id, proveedor_id,
     ruta_imagen, stock_minimo, stock_maximo, activo, fecha_creacion)
VALUES
-- Telas
(1,  'Tela jersey algodón 180g',   1,  1, 1, 'mp/tela_jersey_algodon.jpg',    50.0000,  500.0000, 1, NOW()),
(2,  'Tela mezclilla 12oz',        1,  2, 3, 'mp/tela_mezclilla.jpg',          30.0000,  300.0000, 1, NOW()),
(3,  'Tela gabardina stretch',     1,  1, 1, 'mp/tela_gabardina.jpg',          20.0000,  200.0000, 1, NOW()),
(4,  'Tela polar fleece',          1,  2, 6, 'mp/tela_polar.jpg',              15.0000,  150.0000, 1, NOW()),
(5,  'Tela licra deportiva',       1,  1, 7, 'mp/tela_licra.jpg',              10.0000,  100.0000, 1, NOW()),
(6,  'Tela lino natural',          1,  1, 6, 'mp/tela_lino.jpg',              10.0000,   80.0000, 1, NOW()),
(7,  'Tela popelina blanca',       1,  2, 1, 'mp/tela_popelina.jpg',           20.0000,  200.0000, 1, NOW()),
(8,  'Tela French Terry',          1,  1, 4, 'mp/tela_french_terry.jpg',       15.0000,  150.0000, 1, NOW()),
(9,  'Tela oxford 600D',           1,  2, 3, 'mp/tela_oxford.jpg',             10.0000,   80.0000, 1, NOW()),
(10, 'Tela seda artificial',       1,  1, 1, 'mp/tela_seda.jpg',               5.0000,   50.0000, 1, NOW()),
-- Hilos
(11, 'Hilo poliéster negro 40/2',  4,  4, 2, 'mp/hilo_poliester_negro.jpg',  100.0000,  999.0000, 1, NOW()),
(12, 'Hilo algodón blanco 40/2',   4,  4, 2, 'mp/hilo_algodon_blanco.jpg',   100.0000,  999.0000, 1, NOW()),
(13, 'Hilo overlock gris',         4,  4, 2, 'mp/hilo_overlock.jpg',           50.0000,  500.0000, 1, NOW()),
(14, 'Hilo elástico transparente', 4,  4, 2, 'mp/hilo_elastico.jpg',           20.0000,  200.0000, 1, NOW()),
-- Avíos
(15, 'Cierre metálico 20cm',       4,  5, 8, 'mp/cierre_metalico.jpg',        200.0000, 1000.0000, 1, NOW()),
(16, 'Cierre de plástico 15cm',    4,  5, 8, 'mp/cierre_plastico.jpg',        200.0000, 1000.0000, 1, NOW()),
(17, 'Botón camisa 4 hoyos 12mm',  4,  3, 2, 'mp/boton_camisa.jpg',           500.0000, 5000.0000, 1, NOW()),
(18, 'Botón pantalón metálico',    4,  3, 5, 'mp/boton_pantalon.jpg',         200.0000, 2000.0000, 1, NOW()),
(19, 'Elástico de 3cm',            1,  9, 4, 'mp/elastico_3cm.jpg',            20.0000,  200.0000, 1, NOW()),
(20, 'Etiqueta tejida marca',      4,  6, 4, 'mp/etiqueta_marca.jpg',         500.0000, 5000.0000, 1, NOW()),
(21, 'Etiqueta talla y lavado',    4,  6, 4, 'mp/etiqueta_talla.jpg',         500.0000, 5000.0000, 1, NOW()),
(22, 'Remache metálico dorado',    4, 10, 5, 'mp/remache_dorado.jpg',         300.0000, 3000.0000, 1, NOW()),
(23, 'Hombrera espuma 1cm',        9,  4, 4, 'mp/hombrera.jpg',                20.0000,  200.0000, 1, NOW()),
(24, 'Cordón capucha redondo 1cm', 1,  4, 4, 'mp/cordon_capucha.jpg',          10.0000,  100.0000, 1, NOW()),
(25, 'Entretela termoadherible',   1,  1, 1, 'mp/entretela.jpg',               10.0000,  100.0000, 1, NOW());

-- =============================================================
-- PRODUCTOS
-- =============================================================
INSERT IGNORE INTO producto
    (id, nombre, categoria_id, descripcion, color_id, activo, fecha_creacion)
VALUES
(1,  'Playera Básica',          1, 'Playera cuello redondo 100% algodón',         1, 1, NOW()),
(2,  'Playera Básica',          1, 'Playera cuello redondo 100% algodón',         2, 1, NOW()),
(3,  'Playera Básica',          1, 'Playera cuello redondo 100% algodón',         3, 1, NOW()),
(4,  'Playera Polo',            1, 'Polo piqué manga corta con cuello',           4, 1, NOW()),
(5,  'Playera Polo',            1, 'Polo piqué manga corta con cuello',           1, 1, NOW()),
(6,  'Pantalón Mezclilla Slim', 2, 'Pantalón de mezclilla corte slim',            4, 1, NOW()),
(7,  'Pantalón Mezclilla Slim', 2, 'Pantalón de mezclilla corte slim',            1, 1, NOW()),
(8,  'Pantalón Gabardina',      2, 'Pantalón gabardina stretch corte recto',      3, 1, NOW()),
(9,  'Short Deportivo',         3, 'Short con bolsillos y elástico en cintura',   1, 1, NOW()),
(10, 'Short Deportivo',         3, 'Short con bolsillos y elástico en cintura',   5, 1, NOW()),
(11, 'Sudadera con Capucha',    6, 'Hoodie French Terry unisex',                  1, 1, NOW()),
(12, 'Sudadera con Capucha',    6, 'Hoodie French Terry unisex',                  3, 1, NOW()),
(13, 'Sudadera sin Capucha',    6, 'Crewneck French Terry unisex',                2, 1, NOW()),
(14, 'Chamarra Ligera',         5, 'Chamarra rompevientos con forro',             4, 1, NOW()),
(15, 'Vestido Casual',          4, 'Vestido jersey manga corta midi',             9, 1, NOW()),
(16, 'Blusa Popelina',          7, 'Blusa de popelina con botones frontales',     2, 1, NOW()),
(17, 'Top Deportivo',          10, 'Top licra para actividad física',             5, 1, NOW()),
(18, 'Leggins Deportivos',     10, 'Leggins compresión con bolsillo lateral',     1, 1, NOW()),
(19, 'Pantalón Cargo',          2, 'Pantalón cargo multibolsillos',               6, 1, NOW()),
(20, 'Camiseta Oversize',       1, 'Camiseta holgada unisex longline',            7, 1, NOW());

-- =============================================================
-- ARTÍCULOS (PRODUCTO)  ids 1-60
-- =============================================================
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
-- ARTÍCULOS (MATERIA PRIMA)  ids 101-125
(101, 'MATERIA_PRIMA', 1, NOW()), (102, 'MATERIA_PRIMA', 1, NOW()),
(103, 'MATERIA_PRIMA', 1, NOW()), (104, 'MATERIA_PRIMA', 1, NOW()),
(105, 'MATERIA_PRIMA', 1, NOW()), (106, 'MATERIA_PRIMA', 1, NOW()),
(107, 'MATERIA_PRIMA', 1, NOW()), (108, 'MATERIA_PRIMA', 1, NOW()),
(109, 'MATERIA_PRIMA', 1, NOW()), (110, 'MATERIA_PRIMA', 1, NOW()),
(111, 'MATERIA_PRIMA', 1, NOW()), (112, 'MATERIA_PRIMA', 1, NOW()),
(113, 'MATERIA_PRIMA', 1, NOW()), (114, 'MATERIA_PRIMA', 1, NOW()),
(115, 'MATERIA_PRIMA', 1, NOW()), (116, 'MATERIA_PRIMA', 1, NOW()),
(117, 'MATERIA_PRIMA', 1, NOW()), (118, 'MATERIA_PRIMA', 1, NOW()),
(119, 'MATERIA_PRIMA', 1, NOW()), (120, 'MATERIA_PRIMA', 1, NOW()),
(121, 'MATERIA_PRIMA', 1, NOW()), (122, 'MATERIA_PRIMA', 1, NOW()),
(123, 'MATERIA_PRIMA', 1, NOW()), (124, 'MATERIA_PRIMA', 1, NOW()),
(125, 'MATERIA_PRIMA', 1, NOW());

-- Vincular articulo_id en materia_prima (uno a uno: mp_id N → articulo_id 100+N)
UPDATE materia_prima SET articulo_id = 100 + id WHERE id BETWEEN 1 AND 25;

-- =============================================================
-- PRODUCTO_VARIANTE
-- =============================================================
INSERT IGNORE INTO producto_variante
    (id, articulo_id, producto_id, talla_id, precio_venta, activo, fecha_creacion)
VALUES
-- Playera Básica Negra (prod 1)
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
-- Pantalón Mezclilla Slim Marino (prod 6)
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
-- Leggins Deportivos (prod 18)
(60, 60, 18, 2, 329.00, 1, NOW());

-- =============================================================
-- INVENTARIOS
-- =============================================================
INSERT IGNORE INTO inventarios (id, nombre, tipo, activo, fecha_creacion) VALUES
(1, 'Almacén Principal',          0, 1, NOW()),
(2, 'Almacén Materia Prima',      0, 1, NOW()),
(3, 'Almacén Producto Terminado', 1, 1, NOW()),
(4, 'Almacén Mermas',             0, 1, NOW());

-- =============================================================
-- TIPOS DE MOVIMIENTO
-- =============================================================
INSERT IGNORE INTO tipo_movimientos (id, tipo, signo, activo, fecha_creacion) VALUES
(1, 'Compra',              1,  1, NOW()),
(2, 'Venta',              -1,  1, NOW()),
(3, 'Ajuste positivo',     1,  1, NOW()),
(4, 'Ajuste negativo',    -1,  1, NOW()),
(5, 'Entrada producción',  1,  1, NOW()),
(6, 'Salida producción',  -1,  1, NOW()),
(7, 'Merma',              -1,  1, NOW()),
(8, 'Devolución compra',  -1,  1, NOW()),
(9, 'Devolución venta',    1,  1, NOW());

-- =============================================================
-- CLIENTES
-- =============================================================
INSERT IGNORE INTO cliente
    (id, nombre, correo, contrasenia, telefono, direccion, activo, fecha_creacion)
VALUES
(1,  'María López',       'maria.lopez@gmail.com',   '$2b$12$dummy_hash_1', '4771234567', 'Blvd. López Mateos 100, León, Gto.',     1, NOW()),
(2,  'Carlos Ramírez',    'c.ramirez@hotmail.com',   '$2b$12$dummy_hash_2', '4779876543', 'Av. Insurgentes 250, León, Gto.',         1, NOW()),
(3,  'Ana Martínez',      'ana.mtz@outlook.com',     '$2b$12$dummy_hash_3', '4772345678', 'Calle Hermanos Aldama 45, León, Gto.',    1, NOW()),
(4,  'Jorge Hernández',   'jorge.hdz@gmail.com',     '$2b$12$dummy_hash_4', '4773456789', 'Paseo de los Insurgentes 88, León, Gto.', 1, NOW()),
(5,  'Laura Sánchez',     'lsanchez@yahoo.com.mx',   '$2b$12$dummy_hash_5', '4774567890', 'Blvd. Aeropuerto 320, León, Gto.',        1, NOW()),
(6,  'Roberto García',    'r.garcia@empresa.com',    '$2b$12$dummy_hash_6', '4775678901', 'Av. Tecnológico 500, León, Gto.',         1, NOW()),
(7,  'Sofía Torres',      'sofia.torres@gmail.com',  '$2b$12$dummy_hash_7', '4776789012', 'Calle Pedro Moreno 12, Silao, Gto.',      1, NOW()),
(8,  'Diego Flores',      'dflores@mail.com',        '$2b$12$dummy_hash_8', '4777890123', 'Blvd. Timoteo Lozano 77, León, Gto.',     1, NOW()),
(9,  'Valentina Cruz',    'vcruz@correo.mx',         '$2b$12$dummy_hash_9', '4778901234', 'Av. Juárez 1200, Irapuato, Gto.',         1, NOW()),
(10, 'Miguel Ángel Ruiz', 'maruiz@gmail.com',        '$2b$12$dummy_hash_0', '4770123456', 'Calle Madero 300, Salamanca, Gto.',       1, NOW());

-- =============================================================
-- RECETAS
-- =============================================================
INSERT IGNORE INTO receta
    (id, producto_variante_id, cantidad_base, activo, fecha_creacion)
VALUES
(1, 3,  1, 1, NOW()),   -- Playera Básica Negra M
(2, 8,  1, 1, NOW()),   -- Playera Básica Blanca M
(3, 40, 1, 1, NOW()),   -- Sudadera Capucha Negra M
(4, 34, 1, 1, NOW());   -- Short Deportivo Negro M

-- RECETA DETALLES
INSERT IGNORE INTO receta_detalle
    (id, receta_id, materia_prima_id, cantidad_neta)
VALUES
-- Playera Básica Negra M
(1,  1, 1,  1.6000),
(2,  1, 11, 2.0000),
(3,  1, 13, 1.0000),
(4,  1, 20, 1.0000),
(5,  1, 21, 1.0000),
-- Playera Básica Blanca M
(6,  2, 1,  1.6000),
(7,  2, 12, 2.0000),
(8,  2, 13, 1.0000),
(9,  2, 20, 1.0000),
(10, 2, 21, 1.0000),
-- Sudadera con Capucha Negra M
(11, 3, 8,  2.2000),
(12, 3, 11, 3.0000),
(13, 3, 13, 2.0000),
(14, 3, 19, 0.3000),
(15, 3, 24, 1.5000),
(16, 3, 20, 1.0000),
(17, 3, 21, 1.0000),
-- Short Deportivo Negro M
(18, 4, 5,  0.8000),
(19, 4, 11, 1.0000),
(20, 4, 13, 1.0000),
(21, 4, 19, 0.2500),
(22, 4, 20, 1.0000),
(23, 4, 21, 1.0000);

-- =============================================================
-- COMPRAS
-- =============================================================
INSERT IGNORE INTO compra
    (id, proveedor_id, fecha, total, estatus, observaciones, fecha_creacion)
VALUES
(1, 1, DATE_SUB(NOW(), INTERVAL 45 DAY), 12500.00, 'recibido',    'Pedido quincenal de tela jersey',        NOW()),
(2, 2, DATE_SUB(NOW(), INTERVAL 40 DAY),  3600.00, 'recibido',    'Reposición de hilos y avíos',            NOW()),
(3, 3, DATE_SUB(NOW(), INTERVAL 30 DAY), 18000.00, 'recibido',    'Compra de tela mezclilla importada',     NOW()),
(4, 2, DATE_SUB(NOW(), INTERVAL 20 DAY),  2046.00, 'recibido',    'Botones, etiquetas y cierres',           NOW()),
(5, 6, DATE_SUB(NOW(), INTERVAL 15 DAY),  9500.00, 'recibido',    'Telas naturales: lino y popelina',       NOW()),
(6, 4, DATE_SUB(NOW(), INTERVAL 10 DAY),  6200.00, 'en_transito', 'French Terry y Polar Fleece',            NOW()),
(7, 1, DATE_SUB(NOW(), INTERVAL  5 DAY),  8400.00, 'pendiente',   'Tela jersey para siguiente temporada',   NOW());

INSERT IGNORE INTO compra_detalle
    (id, compra_id, materia_prima_id,
     cantidad_empaque, cantidad_unidad, precio_unitario, subtotal)
VALUES
(1,  1, 1,  2.0000, 100.0000, 125.00, 12500.00),
(2,  2, 11, 10.0000, 10.0000, 180.00,  1800.00),
(3,  2, 12, 10.0000, 10.0000, 180.00,  1800.00),
(4,  3, 2,  3.0000, 300.0000,  60.00, 18000.00),
(5,  4, 17, 2.0000, 288.0000,   4.50,  1296.00),
(6,  4, 20, 1.0000, 500.0000,   1.00,   500.00),
(7,  4, 21, 1.0000, 500.0000,   0.50,   250.00),
(8,  5, 6,  1.0000,  50.0000,  90.00,  4500.00),
(9,  5, 7,  2.0000, 100.0000,  50.00,  5000.00),
(10, 6, 8,  2.0000, 100.0000,  62.00,  6200.00),
(11, 7, 1,  2.0000, 100.0000,  84.00,  8400.00);

-- =============================================================
-- PEDIDOS
-- =============================================================
INSERT IGNORE INTO pedido
    (id, cliente_id, folio, fecha, subtotal, costo_envio, total, estatus, direccion_envio)
VALUES
(1,  1, 'PED-2025-0001', DATE_SUB(NOW(), INTERVAL 30 DAY),  567.00,  99.00,  666.00, 'entregado',  'Blvd. López Mateos 100, León, Gto.'),
(2,  2, 'PED-2025-0002', DATE_SUB(NOW(), INTERVAL 25 DAY),  349.00,   0.00,  349.00, 'entregado',  'Av. Insurgentes 250, León, Gto.'),
(3,  3, 'PED-2025-0003', DATE_SUB(NOW(), INTERVAL 18 DAY),  948.00,  99.00, 1047.00, 'entregado',  'Calle Hermanos Aldama 45, León, Gto.'),
(4,  4, 'PED-2025-0004', DATE_SUB(NOW(), INTERVAL 12 DAY),  599.00,   0.00,  599.00, 'enviado',    'Paseo de los Insurgentes 88, León, Gto.'),
(5,  5, 'PED-2025-0005', DATE_SUB(NOW(), INTERVAL  8 DAY),  798.00,  99.00,  897.00, 'enviado',    'Blvd. Aeropuerto 320, León, Gto.'),
(6,  1, 'PED-2025-0006', DATE_SUB(NOW(), INTERVAL  5 DAY),  599.00,   0.00,  599.00, 'procesando', 'Blvd. López Mateos 100, León, Gto.'),
(7,  6, 'PED-2025-0007', DATE_SUB(NOW(), INTERVAL  3 DAY), 1148.00,  99.00, 1247.00, 'procesando', 'Av. Tecnológico 500, León, Gto.'),
(8,  7, 'PED-2025-0008', DATE_SUB(NOW(), INTERVAL  1 DAY),  379.00,  99.00,  478.00, 'pendiente',  'Calle Pedro Moreno 12, Silao, Gto.'),
(9,  8, 'PED-2025-0009', NOW(),                            1199.00,   0.00, 1199.00, 'pendiente',  'Blvd. Timoteo Lozano 77, León, Gto.'),
(10, 9, 'PED-2025-0010', NOW(),                             499.00,  99.00,  598.00, 'pendiente',  'Av. Juárez 1200, Irapuato, Gto.');

INSERT IGNORE INTO pedido_detalle
    (id, pedido_id, producto_variante_id, cantidad, precio_unitario, subtotal)
VALUES
(1,  1, 3,  2, 189.00, 378.00),
(2,  1, 34, 1, 189.00, 189.00),
(3,  2, 15, 1, 349.00, 349.00),
(4,  3, 40, 1, 599.00, 599.00),
(5,  3, 3,  1, 189.00, 189.00),
(6,  3, 34, 1, 249.00, 249.00),
(7,  4, 22, 1, 599.00, 599.00),
(8,  5, 43, 1, 599.00, 599.00),
(9,  5, 11, 1, 199.00, 199.00),
(10, 6, 24, 1, 599.00, 599.00),
(11, 7, 39, 1, 599.00, 599.00),
(12, 7, 48, 1, 549.00, 549.00),
(13, 8, 54, 1, 379.00, 379.00),
(14, 9, 41, 1, 599.00, 599.00),
(15, 9, 42, 1, 629.00, 629.00),
(16,10, 51, 1, 499.00, 499.00);

-- =============================================================
-- PAGOS
-- =============================================================
INSERT IGNORE INTO pago
    (id, pedido_id, metodo, referencia, monto, estatus, fecha)
VALUES
(1,  1, 'tarjeta',       'TXN-4A2F91',   666.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 30 DAY)),
(2,  2, 'transferencia', 'REF-882341',    349.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 25 DAY)),
(3,  3, 'tarjeta',       'TXN-7B3C44',  1047.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 18 DAY)),
(4,  4, 'tarjeta',       'TXN-9D1E22',   599.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL 12 DAY)),
(5,  5, 'oxxo',          'OXXO-55512',   897.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL  8 DAY)),
(6,  6, 'transferencia', 'REF-991022',   599.00, 'aprobado',  DATE_SUB(NOW(), INTERVAL  5 DAY)),
(7,  7, 'tarjeta',       'TXN-1F8A77',  1247.00, 'pendiente', DATE_SUB(NOW(), INTERVAL  3 DAY)),
(8,  8, 'simulado',      NULL,            478.00, 'pendiente', DATE_SUB(NOW(), INTERVAL  1 DAY)),
(9,  9, 'simulado',      NULL,           1199.00, 'pendiente', NOW()),
(10,10, 'oxxo',          'OXXO-88832',   598.00, 'pendiente', NOW());

-- =============================================================
-- RESEÑAS
-- =============================================================
INSERT IGNORE INTO resenia
    (id, cliente_id, producto_id, calificacion, comentario, verificada, fecha)
VALUES
(1, 1,  1, 5, 'Excelente calidad, el algodón es muy suave y la talla M me quedó perfecto.',           1, DATE_SUB(NOW(), INTERVAL 28 DAY)),
(2, 2,  4, 4, 'Muy buen polo, se ve elegante. Le doy 4 porque tardó un poco en llegar.',              1, DATE_SUB(NOW(), INTERVAL 22 DAY)),
(3, 3, 11, 5, 'La sudadera es increíble, muy abrigadora y el material no se destiñe.',                1, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(4, 4,  6, 4, 'Buen pantalón, cae muy bien. El azul marino es idéntico a las fotos.',                 1, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(5, 5, 12, 3, 'La calidad es buena pero el gris me llegó un poco más oscuro de lo esperado.',         1, DATE_SUB(NOW(), INTERVAL  6 DAY)),
(6, 6, 11, 5, 'Segunda compra de esta sudadera, sin duda la mejor que he tenido.',                    0, DATE_SUB(NOW(), INTERVAL  2 DAY)),
(7, 7, 16, 5, 'La blusa es preciosa, perfecta para la oficina. El popelín es de buena calidad.',      0, DATE_SUB(NOW(), INTERVAL  1 DAY)),
(8, 1,  9, 4, 'El short es muy cómodo para hacer ejercicio, el elástico no aprieta.',                 1, DATE_SUB(NOW(), INTERVAL 25 DAY));


-- =============================================================
-- MOVIMIENTOS DE INVENTARIO
-- Se registran las entradas por compra y salidas por venta
-- para tener trazabilidad en movimientos_inventario
-- =============================================================

-- Entradas de materia prima (compras recibidas) → inv 2
INSERT IGNORE INTO movimientos_inventario
    (id, articulo_id, tipo_mov_id, inv_id, cantidad, unidad_id, empaque_id, signo, existencia)
VALUES
-- Compra 1: Tela jersey (MP 1 → art 101)
(1,  101, 1, 2, 100.00, 1, 1,  1, 100.00),
-- Compra 2: Hilo negro y blanco
(2,  111, 1, 2,  10.00, 4, 4,  1,  10.00),
(3,  112, 1, 2,  10.00, 4, 4,  1,  10.00),
-- Compra 3: Mezclilla
(4,  102, 1, 2, 300.00, 1, 2,  1, 300.00),
-- Compra 4: Botones y etiquetas
(5,  117, 1, 2, 288.00, 4, 3,  1, 288.00),
(6,  120, 1, 2, 500.00, 4, 6,  1, 500.00),
(7,  121, 1, 2, 500.00, 4, 6,  1, 500.00),
-- Compra 5: Lino y popelina
(8,  106, 1, 2,  50.00, 1, 1,  1,  50.00),
(9,  107, 1, 2, 100.00, 1, 2,  1, 100.00),
-- Salidas producción (órdenes completadas) → consumen de inv 2
-- OP 1: 50 Playeras negras M  → 50×1.6m tela + 50×2 hilo + 50×1 overlock + 50×1 et.marca + 50×1 et.talla
(10, 101, 6, 2,  80.00, 1, NULL, -1,  20.00),
(11, 111, 6, 2, 100.00, 4, NULL, -1,   0.00),   -- hilo negro
(12, 113, 6, 2,  50.00, 4, NULL, -1,   0.00),   -- overlock
(13, 120, 6, 2,  50.00, 4, NULL, -1, 450.00),
(14, 121, 6, 2,  50.00, 4, NULL, -1, 450.00),
-- OP 2: 30 Playeras blancas M
(15, 101, 6, 2,  48.00, 1, NULL, -1,   0.00),   -- 30×1.6m
(16, 112, 6, 2,  60.00, 4, NULL, -1,   0.00),   -- hilo blanco
(17, 113, 6, 2,  30.00, 4, NULL, -1,   0.00),
(18, 120, 6, 2,  30.00, 4, NULL, -1, 420.00),
(19, 121, 6, 2,  30.00, 4, NULL, -1, 420.00),
-- Entradas producto terminado OP1+OP2 → inv 3
(20,  3,  5, 3,  50.00, 4, NULL,  1,  50.00),   -- art 3 = variante pv3 (playera negra M)
(21,  8,  5, 3,  30.00, 4, NULL,  1,  30.00),   -- art 8 = variante pv8 (playera blanca M)
-- Salidas venta → inv 3
(22,  3,  2, 3,   2.00, 4, NULL, -1,  48.00),   -- pedido 1 det 1 (2 playeras negras M)
(23, 34,  2, 3,   1.00, 4, NULL, -1,  29.00),   -- pedido 1 det 2
(24, 15,  2, 3,   1.00, 4, NULL, -1,  29.00),   -- pedido 2
(25, 40,  2, 3,   1.00, 4, NULL, -1,  19.00),   -- pedido 3
(26,  3,  2, 3,   1.00, 4, NULL, -1,  47.00),   -- pedido 3
(27, 34,  2, 3,   1.00, 4, NULL, -1,  28.00);   -- pedido 3

-- =============================================================
-- STOCK ARTÍCULO
-- Snapshot del inventario actual tras movimientos anteriores
-- inv 2 = Materia Prima  |  inv 3 = Producto Terminado
-- =============================================================

-- ── Materia Prima (inv 2) ──────────────────────────────────
INSERT IGNORE INTO stock_articulo (articulo_id, inv_id, cantidad, fecha_creacion) VALUES
-- Telas (art 101-110)
(101, 2,  72.0000, NOW()),   -- jersey algodón: 100 comprada - 80 OP1 - 48 OP2 + 100 pedido pendiente*
                              -- * simplificado: dejamos stock realista post-producción
(102, 2, 300.0000, NOW()),   -- mezclilla: comprada, no consumida aún
(103, 2,   0.0000, NOW()),   -- gabardina: sin compra aún
(104, 2,   0.0000, NOW()),   -- polar: sin compra aún
(105, 2,   0.0000, NOW()),   -- licra: sin compra aún
(106, 2,  50.0000, NOW()),   -- lino
(107, 2, 100.0000, NOW()),   -- popelina
(108, 2, 100.0000, NOW()),   -- French Terry (compra en tránsito, registrado como disponible)
(109, 2,   0.0000, NOW()),
(110, 2,   0.0000, NOW()),
-- Hilos (art 111-114)
(111, 2,   0.0000, NOW()),   -- hilo negro: consumido en producción
(112, 2,   0.0000, NOW()),   -- hilo blanco: consumido
(113, 2,   0.0000, NOW()),   -- overlock: consumido
(114, 2,   0.0000, NOW()),
-- Avíos (art 115-125)
(115, 2,   0.0000, NOW()),
(116, 2,   0.0000, NOW()),
(117, 2, 288.0000, NOW()),   -- botón camisa
(118, 2,   0.0000, NOW()),
(119, 2,   0.0000, NOW()),   -- elástico
(120, 2, 420.0000, NOW()),   -- etiqueta marca: 500 - 50 OP1 - 30 OP2
(121, 2, 420.0000, NOW()),   -- etiqueta talla
(122, 2,   0.0000, NOW()),
(123, 2,   0.0000, NOW()),
(124, 2,   0.0000, NOW()),
(125, 2,   0.0000, NOW()),

-- ── Producto Terminado (inv 3) ────────────────────────────
-- Solo variantes con stock producido y/o vendido
(3,  3,  47.0000, NOW()),   -- pv3  Playera Negra M:     50 - 2 ped1 - 1 ped3
(8,  3,  29.0000, NOW()),   -- pv8  Playera Blanca M:    30 - 1 ped2
(15, 3,  28.0000, NOW()),   -- pv15 Polo Marino S (via ped2 — ajuste, estaba en stock previo)
(34, 3,  27.0000, NOW()),   -- pv34 Short Negro M:       30 - 1 ped1 - 1 ped3 + prod anterior
(40, 3,  19.0000, NOW()),   -- pv40 Sudadera Negra M:    20 - 1 ped3
-- Variantes con stock por ajuste / producción previa (para dar vida al catálogo)
(1,  3,  15.0000, NOW()),   -- pv1  Playera Negra XS
(2,  3,  25.0000, NOW()),   -- pv2  Playera Negra S
(4,  3,  18.0000, NOW()),   -- pv4  Playera Negra L
(5,  3,  10.0000, NOW()),   -- pv5  Playera Negra XL
(7,  3,  20.0000, NOW()),   -- pv7  Playera Blanca S
(9,  3,  15.0000, NOW()),   -- pv9  Playera Blanca L
(11, 3,  22.0000, NOW()),   -- pv11 Playera Gris S
(12, 3,  20.0000, NOW()),   -- pv12 Playera Gris M
(13, 3,  18.0000, NOW()),   -- pv13 Playera Gris L
(14, 3,  12.0000, NOW()),   -- pv14 Polo Marino S
(21, 3,  10.0000, NOW()),   -- pv21 Pantalón Mezclilla 28
(22, 3,  14.0000, NOW()),   -- pv22 Pantalón Mezclilla 30
(23, 3,  12.0000, NOW()),   -- pv23 Pantalón Mezclilla 32
(33, 3,  20.0000, NOW()),   -- pv33 Short Negro S
(35, 3,  18.0000, NOW()),   -- pv35 Short Negro L
(39, 3,  15.0000, NOW()),   -- pv39 Sudadera Negra S
(41, 3,  16.0000, NOW()),   -- pv41 Sudadera Negra L
(43, 3,  14.0000, NOW()),   -- pv43 Sudadera Gris M
(45, 3,  12.0000, NOW()),   -- pv45 Sudadera sin Capucha S
(46, 3,  15.0000, NOW()),   -- pv46 Sudadera sin Capucha M
(51, 3,   8.0000, NOW()),   -- pv51 Vestido Rosa XS
(52, 3,  10.0000, NOW()),   -- pv52 Vestido Rosa S
(53, 3,  12.0000, NOW()),   -- pv53 Vestido Rosa M
(54, 3,  10.0000, NOW()),   -- pv54 Blusa Popelina XS
(55, 3,  12.0000, NOW()),   -- pv55 Blusa Popelina S
(56, 3,  10.0000, NOW()),   -- pv56 Blusa Popelina M
(57, 3,  15.0000, NOW()),   -- pv57 Top Deportivo XS
(58, 3,  18.0000, NOW()),   -- pv58 Top Deportivo S
(59, 3,  14.0000, NOW()),   -- pv59 Top Deportivo M
(60, 3,  20.0000, NOW());   -- pv60 Leggins S

-- =============================================================
SET FOREIGN_KEY_CHECKS = 1;
-- FIN DEL SEED
-- =============================================================