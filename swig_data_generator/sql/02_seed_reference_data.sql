-- Swig Operations Database - Reference Data Seed
-- Real Swig menu items and operational data

-- =============================================================================
-- STORES (3 Utah locations)
-- =============================================================================

INSERT INTO Organization_Stores VALUES
(1001, 'Swig - St. George Main', '929 W Sunset Blvd', 'St. George', 'UT', '84770', 37.1041, -113.5841, 'America/Denver', '06:00:00', '22:00:00', true, '2020-03-15'),
(1002, 'Swig - Provo Center', '1283 N University Ave', 'Provo', 'UT', '84604', 40.2338, -111.6585, 'America/Denver', '06:00:00', '22:00:00', true, '2019-06-01'),
(1003, 'Swig - Draper', '12234 S Draper Gate Dr', 'Draper', 'UT', '84020', 40.5247, -111.8638, 'America/Denver', '06:00:00', '22:00:00', true, '2021-01-10');

-- =============================================================================
-- PRODUCT CATEGORIES
-- =============================================================================

INSERT INTO Product_Categories VALUES
(1, 'Signature Drinks', 1),
(2, 'Dirty Sodas', 2),
(3, 'Refreshers', 3),
(4, 'Infusions', 4),
(5, 'Energy', 5),
(6, 'Creams & Add-Ins', 6),
(7, 'Syrups', 7),
(8, 'Purees', 8),
(9, 'Food', 9),
(10, 'Merchandise', 10);

-- =============================================================================
-- PRODUCT CATALOG - Real Swig Menu Items
-- =============================================================================

-- Signature Drinks (Base Beverages)
INSERT INTO Product_Catalog VALUES
('SIG001', 'Texas Tab', 1, 'Base_Beverage', 4.29, true, 180, 44, false, 'Dr Pepper with vanilla and coconut cream'),
('SIG002', 'Raspberry Dream', 1, 'Base_Beverage', 4.29, true, 200, 44, false, 'Dr Pepper with raspberry puree and coconut cream'),
('SIG003', 'Island Dream', 1, 'Base_Beverage', 4.29, true, 190, 44, false, 'Sprite with coconut and pineapple'),
('SIG004', 'The Founder', 1, 'Base_Beverage', 4.29, true, 170, 44, false, 'Diet Coke with coconut and lime'),
('SIG005', 'Dirty Dr Pepper', 1, 'Base_Beverage', 3.99, true, 185, 44, false, 'Dr Pepper with coconut cream'),
('SIG006', 'Miami Vice', 1, 'Base_Beverage', 4.29, true, 195, 44, false, 'Sprite with strawberry and coconut'),
('SIG007', 'The Refresher', 1, 'Base_Beverage', 4.49, true, 160, 44, false, 'Sprite with fresh lime and coconut'),
('SIG008', 'Peach Ring', 1, 'Base_Beverage', 4.29, true, 175, 44, false, 'Sprite with peach puree'),
('SIG009', 'Blue Coconut', 1, 'Base_Beverage', 4.29, true, 185, 44, false, 'Sprite with blue raspberry and coconut'),
('SIG010', 'Sunset', 1, 'Base_Beverage', 4.29, true, 190, 44, false, 'Lemonade with strawberry puree');

-- Regular Sodas (Base for custom drinks)
INSERT INTO Product_Catalog VALUES
('BASE001', 'Dr Pepper', 2, 'Base_Beverage', 2.99, true, 150, 44, false, 'Classic Dr Pepper'),
('BASE002', 'Diet Dr Pepper', 2, 'Base_Beverage', 2.99, true, 0, 44, true, 'Diet Dr Pepper'),
('BASE003', 'Coca-Cola', 2, 'Base_Beverage', 2.99, true, 140, 44, false, 'Classic Coca-Cola'),
('BASE004', 'Diet Coke', 2, 'Base_Beverage', 2.99, true, 0, 44, true, 'Diet Coke'),
('BASE005', 'Sprite', 2, 'Base_Beverage', 2.99, true, 140, 44, false, 'Classic Sprite'),
('BASE006', 'Sprite Zero', 2, 'Base_Beverage', 2.99, true, 0, 44, true, 'Sprite Zero Sugar'),
('BASE007', 'Mountain Dew', 2, 'Base_Beverage', 2.99, true, 170, 44, false, 'Mountain Dew'),
('BASE008', 'Diet Mountain Dew', 2, 'Base_Beverage', 2.99, true, 0, 44, true, 'Diet Mountain Dew'),
('BASE009', 'Lemonade', 3, 'Base_Beverage', 3.29, true, 120, 44, false, 'Fresh Lemonade'),
('BASE010', 'Water', 3, 'Base_Beverage', 1.99, true, 0, 44, true, 'Bottled Water');

-- Energy Drinks (Revivers)
INSERT INTO Product_Catalog VALUES
('ENG001', 'Reviver Original', 5, 'Base_Beverage', 4.99, true, 150, 32, false, 'Energy drink with coconut'),
('ENG002', 'Reviver Tropical', 5, 'Base_Beverage', 4.99, true, 160, 32, false, 'Tropical energy blend'),
('ENG003', 'Reviver Berry', 5, 'Base_Beverage', 4.99, true, 155, 32, false, 'Berry energy blend'),
('ENG004', 'Reviver Sugar Free', 5, 'Base_Beverage', 4.99, true, 10, 32, true, 'Sugar free energy');

-- Modifiers - Creams
INSERT INTO Product_Catalog VALUES
('MOD001', 'Coconut Cream', 6, 'Modifier', 0.79, true, 40, null, false, 'Classic coconut cream'),
('MOD002', 'Half & Half Cream', 6, 'Modifier', 0.79, true, 45, null, false, 'Half and half cream'),
('MOD003', 'Heavy Cream', 6, 'Modifier', 0.89, true, 60, null, false, 'Heavy whipping cream'),
('MOD004', 'Oat Milk', 6, 'Modifier', 0.99, true, 30, null, false, 'Oat milk alternative'),
('MOD005', 'Almond Milk', 6, 'Modifier', 0.99, true, 15, null, true, 'Almond milk alternative');

-- Modifiers - Syrups
INSERT INTO Product_Catalog VALUES
('SYR001', 'Vanilla Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Vanilla flavoring'),
('SYR002', 'Raspberry Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Raspberry flavoring'),
('SYR003', 'Coconut Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Coconut flavoring'),
('SYR004', 'Peach Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Peach flavoring'),
('SYR005', 'Mango Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Mango flavoring'),
('SYR006', 'Strawberry Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Strawberry flavoring'),
('SYR007', 'Blue Raspberry Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Blue raspberry flavoring'),
('SYR008', 'Cherry Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Cherry flavoring'),
('SYR009', 'Lime Syrup', 7, 'Modifier', 0.69, true, 25, null, false, 'Lime flavoring'),
('SYR010', 'Sugar Free Vanilla', 7, 'Modifier', 0.69, true, 0, null, true, 'Sugar free vanilla'),
('SYR011', 'Sugar Free Raspberry', 7, 'Modifier', 0.69, true, 0, null, true, 'Sugar free raspberry'),
('SYR012', 'Sugar Free Coconut', 7, 'Modifier', 0.69, true, 0, null, true, 'Sugar free coconut');

-- Modifiers - Purees
INSERT INTO Product_Catalog VALUES
('PUR001', 'Raspberry Puree', 8, 'Modifier', 0.89, true, 30, null, false, 'Fresh raspberry puree'),
('PUR002', 'Peach Puree', 8, 'Modifier', 0.89, true, 30, null, false, 'Fresh peach puree'),
('PUR003', 'Strawberry Puree', 8, 'Modifier', 0.89, true, 30, null, false, 'Fresh strawberry puree'),
('PUR004', 'Mango Puree', 8, 'Modifier', 0.89, true, 30, null, false, 'Fresh mango puree'),
('PUR005', 'Pineapple Puree', 8, 'Modifier', 0.89, true, 30, null, false, 'Fresh pineapple puree');

-- Modifiers - Other
INSERT INTO Product_Catalog VALUES
('ADD001', 'Fresh Lime', 6, 'Modifier', 0.49, true, 5, null, false, 'Fresh lime wedge'),
('ADD002', 'Fresh Lemon', 6, 'Modifier', 0.49, true, 5, null, false, 'Fresh lemon wedge'),
('ADD003', 'Energy Shot', 6, 'Modifier', 1.49, true, 80, null, false, 'Energy boost shot'),
('ADD004', 'Extra Ice', 6, 'Modifier', 0.00, true, 0, null, false, 'Extra pebble ice'),
('ADD005', 'Light Ice', 6, 'Modifier', 0.00, true, 0, null, false, 'Light ice');

-- Food Items
INSERT INTO Product_Catalog VALUES
('FOOD001', 'Sugar Cookie', 9, 'Food', 2.49, true, 280, null, false, 'Fresh baked sugar cookie'),
('FOOD002', 'Chocolate Chip Cookie', 9, 'Food', 2.49, true, 320, null, false, 'Fresh baked chocolate chip'),
('FOOD003', 'Pretzel Bites', 9, 'Food', 4.29, true, 380, null, false, 'Warm pretzel bites with cheese'),
('FOOD004', 'Cookie Dough Bites', 9, 'Food', 3.99, true, 350, null, false, 'Edible cookie dough'),
('FOOD005', 'Brownie', 9, 'Food', 2.99, true, 340, null, false, 'Chocolate brownie');

-- =============================================================================
-- JOB ROLES
-- =============================================================================

INSERT INTO Job_Roles VALUES
('GM', 'General Manager', 22.00, true, true, 18),
('ASM', 'Assistant Manager', 17.00, true, true, 18),
('SHIFT', 'Shift Lead', 14.50, true, true, 18),
('MIX', 'Mixologist', 12.00, false, true, 16),
('RUNNER', 'Runner/Linebuster', 11.50, false, false, 16),
('TRAIN', 'Trainee', 11.00, false, false, 16);

-- =============================================================================
-- VENDORS
-- =============================================================================

INSERT INTO Vendors VALUES
(1, 'Sysco Foods', 'Mike Johnson', 'mike.j@sysco.com', '801-555-0101', 2, true),
(2, 'Nicholas & Company', 'Sarah Williams', 'swilliams@nicholas.com', '801-555-0102', 3, true),
(3, 'Torani Syrups Direct', 'Orders Dept', 'orders@torani.com', '800-555-0103', 5, true),
(4, 'Coca-Cola Bottling', 'Account Team', 'accounts@cocacola.com', '801-555-0104', 1, true),
(5, 'Dr Pepper Snapple', 'Regional Sales', 'regional@drpepper.com', '801-555-0105', 1, true);

-- =============================================================================
-- INVENTORY ITEMS
-- =============================================================================

-- Syrups (Torani)
INSERT INTO Inventory_Item_Master VALUES
(101, 'Torani Vanilla Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 6, 3, true),
(102, 'Torani Raspberry Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 6, 3, true),
(103, 'Torani Coconut Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 6, 3, true),
(104, 'Torani Peach Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 4, 2, true),
(105, 'Torani Mango Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 4, 2, true),
(106, 'Torani Strawberry Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 6, 3, true),
(107, 'Torani Blue Raspberry Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 4, 2, true),
(108, 'Torani Cherry Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 4, 2, true),
(109, 'Torani Lime Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 8.99, 4, 2, true),
(110, 'Torani SF Vanilla Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 9.49, 3, 2, true),
(111, 'Torani SF Raspberry Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 9.49, 3, 2, true),
(112, 'Torani SF Coconut Syrup', 'Syrup', 3, 'Bottle', 'pump', 25.0, 9.49, 3, 2, true);

-- Purees
INSERT INTO Inventory_Item_Master VALUES
(201, 'Raspberry Puree', 'Puree', 2, 'Bottle', 'oz', 32.0, 12.99, 8, 4, true),
(202, 'Peach Puree', 'Puree', 2, 'Bottle', 'oz', 32.0, 12.99, 6, 3, true),
(203, 'Strawberry Puree', 'Puree', 2, 'Bottle', 'oz', 32.0, 12.99, 8, 4, true),
(204, 'Mango Puree', 'Puree', 2, 'Bottle', 'oz', 32.0, 12.99, 6, 3, true),
(205, 'Pineapple Puree', 'Puree', 2, 'Bottle', 'oz', 32.0, 12.99, 4, 2, true);

-- Dairy/Creams
INSERT INTO Inventory_Item_Master VALUES
(301, 'Coconut Cream', 'Dairy', 2, 'Carton', 'oz', 64.0, 6.99, 12, 6, true),
(302, 'Half & Half', 'Dairy', 1, 'Carton', 'oz', 64.0, 4.99, 8, 4, true),
(303, 'Heavy Cream', 'Dairy', 1, 'Carton', 'oz', 32.0, 5.99, 6, 3, true),
(304, 'Oat Milk', 'Dairy', 2, 'Carton', 'oz', 64.0, 5.49, 4, 2, true),
(305, 'Almond Milk', 'Dairy', 2, 'Carton', 'oz', 64.0, 4.99, 4, 2, true);

-- Base Carbonated (BIB - Bag in Box)
INSERT INTO Inventory_Item_Master VALUES
(401, 'Dr Pepper BIB', 'Base_Carbonated', 5, 'BIB', 'oz', 640.0, 89.99, 4, 2, true),
(402, 'Diet Dr Pepper BIB', 'Base_Carbonated', 5, 'BIB', 'oz', 640.0, 89.99, 2, 1, true),
(403, 'Coca-Cola BIB', 'Base_Carbonated', 4, 'BIB', 'oz', 640.0, 79.99, 3, 2, true),
(404, 'Diet Coke BIB', 'Base_Carbonated', 4, 'BIB', 'oz', 640.0, 79.99, 3, 2, true),
(405, 'Sprite BIB', 'Base_Carbonated', 4, 'BIB', 'oz', 640.0, 79.99, 4, 2, true),
(406, 'Sprite Zero BIB', 'Base_Carbonated', 4, 'BIB', 'oz', 640.0, 79.99, 2, 1, true),
(407, 'Mountain Dew BIB', 'Base_Carbonated', 5, 'BIB', 'oz', 640.0, 84.99, 2, 1, true),
(408, 'Lemonade Concentrate', 'Base_Carbonated', 1, 'Bottle', 'oz', 128.0, 24.99, 6, 3, true);

-- Energy
INSERT INTO Inventory_Item_Master VALUES
(501, 'Energy Base Concentrate', 'Energy', 2, 'Bottle', 'oz', 64.0, 34.99, 4, 2, true);

-- Paper Goods
INSERT INTO Inventory_Item_Master VALUES
(601, '44oz Cups', 'Paper_Goods', 1, 'Sleeve', 'count', 50.0, 12.99, 20, 10, true),
(602, '32oz Cups', 'Paper_Goods', 1, 'Sleeve', 'count', 50.0, 10.99, 15, 8, true),
(603, 'Dome Lids 44oz', 'Paper_Goods', 1, 'Sleeve', 'count', 50.0, 8.99, 20, 10, true),
(604, 'Dome Lids 32oz', 'Paper_Goods', 1, 'Sleeve', 'count', 50.0, 7.99, 15, 8, true),
(605, 'Straws', 'Paper_Goods', 1, 'Box', 'count', 500.0, 14.99, 4, 2, true),
(606, 'Napkins', 'Paper_Goods', 1, 'Pack', 'count', 250.0, 6.99, 8, 4, true);

-- Food Prep
INSERT INTO Inventory_Item_Master VALUES
(701, 'Sugar Cookie Dough (Frozen)', 'Food_Prep', 1, 'Case', 'count', 48.0, 45.99, 2, 1, true),
(702, 'Chocolate Chip Cookie Dough', 'Food_Prep', 1, 'Case', 'count', 48.0, 47.99, 2, 1, true),
(703, 'Pretzel Bites (Frozen)', 'Food_Prep', 1, 'Bag', 'count', 100.0, 24.99, 4, 2, true),
(704, 'Edible Cookie Dough', 'Food_Prep', 2, 'Container', 'oz', 32.0, 18.99, 3, 2, true),
(705, 'Brownies (Frozen)', 'Food_Prep', 1, 'Case', 'count', 24.0, 34.99, 2, 1, true),
(706, 'Cheese Sauce', 'Food_Prep', 1, 'Can', 'oz', 32.0, 8.99, 4, 2, true);

-- Ice
INSERT INTO Inventory_Item_Master VALUES
(801, 'Pebble Ice', 'Ice', 1, 'Bag', 'lb', 20.0, 4.99, 10, 5, true);

-- Fresh Items
INSERT INTO Inventory_Item_Master VALUES
(901, 'Fresh Limes', 'Food_Prep', 1, 'Box', 'count', 48.0, 18.99, 2, 1, true),
(902, 'Fresh Lemons', 'Food_Prep', 1, 'Box', 'count', 48.0, 16.99, 1, 1, true);

-- =============================================================================
-- RECIPE BOM MAPPING (Product to Ingredients)
-- =============================================================================

-- Texas Tab (Dr Pepper + Vanilla + Coconut Cream)
INSERT INTO Recipe_BOM_Mapping VALUES
(1, 'SIG001', 401, 12.0, 'oz', 0.02, false),
(2, 'SIG001', 101, 2.0, 'pump', 0.05, false),
(3, 'SIG001', 301, 1.5, 'oz', 0.03, false),
(4, 'SIG001', 601, 1.0, 'count', 0.0, false),
(5, 'SIG001', 603, 1.0, 'count', 0.0, false),
(6, 'SIG001', 605, 1.0, 'count', 0.0, false);

-- Raspberry Dream (Dr Pepper + Raspberry Puree + Coconut Cream)
INSERT INTO Recipe_BOM_Mapping VALUES
(7, 'SIG002', 401, 12.0, 'oz', 0.02, false),
(8, 'SIG002', 201, 1.0, 'oz', 0.03, false),
(9, 'SIG002', 301, 1.5, 'oz', 0.03, false),
(10, 'SIG002', 601, 1.0, 'count', 0.0, false),
(11, 'SIG002', 603, 1.0, 'count', 0.0, false),
(12, 'SIG002', 605, 1.0, 'count', 0.0, false);

-- Island Dream (Sprite + Coconut Syrup + Pineapple Puree)
INSERT INTO Recipe_BOM_Mapping VALUES
(13, 'SIG003', 405, 12.0, 'oz', 0.02, false),
(14, 'SIG003', 103, 2.0, 'pump', 0.05, false),
(15, 'SIG003', 205, 1.0, 'oz', 0.03, false),
(16, 'SIG003', 601, 1.0, 'count', 0.0, false),
(17, 'SIG003', 603, 1.0, 'count', 0.0, false),
(18, 'SIG003', 605, 1.0, 'count', 0.0, false);

-- The Founder (Diet Coke + Coconut Cream + Fresh Lime)
INSERT INTO Recipe_BOM_Mapping VALUES
(19, 'SIG004', 404, 12.0, 'oz', 0.02, false),
(20, 'SIG004', 301, 1.5, 'oz', 0.03, false),
(21, 'SIG004', 901, 0.25, 'count', 0.1, false),
(22, 'SIG004', 601, 1.0, 'count', 0.0, false),
(23, 'SIG004', 603, 1.0, 'count', 0.0, false),
(24, 'SIG004', 605, 1.0, 'count', 0.0, false);

-- Dirty Dr Pepper (Dr Pepper + Coconut Cream)
INSERT INTO Recipe_BOM_Mapping VALUES
(25, 'SIG005', 401, 12.0, 'oz', 0.02, false),
(26, 'SIG005', 301, 1.5, 'oz', 0.03, false),
(27, 'SIG005', 601, 1.0, 'count', 0.0, false),
(28, 'SIG005', 603, 1.0, 'count', 0.0, false),
(29, 'SIG005', 605, 1.0, 'count', 0.0, false);

-- Base Sodas (just the base + cup)
INSERT INTO Recipe_BOM_Mapping VALUES
(30, 'BASE001', 401, 12.0, 'oz', 0.02, false),
(31, 'BASE001', 601, 1.0, 'count', 0.0, false),
(32, 'BASE001', 603, 1.0, 'count', 0.0, false),
(33, 'BASE001', 605, 1.0, 'count', 0.0, false);

INSERT INTO Recipe_BOM_Mapping VALUES
(34, 'BASE004', 404, 12.0, 'oz', 0.02, false),
(35, 'BASE004', 601, 1.0, 'count', 0.0, false),
(36, 'BASE004', 603, 1.0, 'count', 0.0, false),
(37, 'BASE004', 605, 1.0, 'count', 0.0, false);

INSERT INTO Recipe_BOM_Mapping VALUES
(38, 'BASE005', 405, 12.0, 'oz', 0.02, false),
(39, 'BASE005', 601, 1.0, 'count', 0.0, false),
(40, 'BASE005', 603, 1.0, 'count', 0.0, false),
(41, 'BASE005', 605, 1.0, 'count', 0.0, false);

-- Modifiers (standalone usage tracking)
INSERT INTO Recipe_BOM_Mapping VALUES
(42, 'MOD001', 301, 1.5, 'oz', 0.03, false),
(43, 'MOD002', 302, 1.5, 'oz', 0.03, false),
(44, 'MOD003', 303, 1.5, 'oz', 0.03, false),
(45, 'SYR001', 101, 2.0, 'pump', 0.05, false),
(46, 'SYR002', 102, 2.0, 'pump', 0.05, false),
(47, 'SYR003', 103, 2.0, 'pump', 0.05, false),
(48, 'PUR001', 201, 1.0, 'oz', 0.03, false),
(49, 'PUR002', 202, 1.0, 'oz', 0.03, false),
(50, 'PUR003', 203, 1.0, 'oz', 0.03, false);

-- Food Items
INSERT INTO Recipe_BOM_Mapping VALUES
(51, 'FOOD001', 701, 1.0, 'count', 0.02, false),
(52, 'FOOD002', 702, 1.0, 'count', 0.02, false),
(53, 'FOOD003', 703, 8.0, 'count', 0.05, false),
(54, 'FOOD003', 706, 2.0, 'oz', 0.05, false),
(55, 'FOOD004', 704, 4.0, 'oz', 0.03, false),
(56, 'FOOD005', 705, 1.0, 'count', 0.02, false);

-- =============================================================================
-- DISCOUNTS AND PROMOTIONS
-- =============================================================================

INSERT INTO Discounts_Promotions VALUES
(1, 'HAPPYHOUR', 'Happy Hour 2-4pm', 'Percent_Off', 20.00, 0, 'ALL', '2025-01-01', '2025-12-31', true, 0),
(2, 'FIRSTSWIG', 'First Time Customer', 'Dollar_Off', 2.00, 5.00, 'ALL', '2025-01-01', '2025-12-31', true, 0),
(3, 'BOGO50', 'Buy One Get One 50% Off', 'BOGO', 50.00, 0, 'Base_Beverage', '2025-01-01', '2025-03-31', true, 0),
(4, 'FREECOOKIE', 'Free Cookie with Drink', 'Free_Item', 0, 4.00, 'FOOD001', '2025-01-01', '2025-12-31', true, 0);
