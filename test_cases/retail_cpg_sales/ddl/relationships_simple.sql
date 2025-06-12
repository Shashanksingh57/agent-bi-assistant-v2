-- RETAIL CPG SALES RELATIONSHIPS
-- Simple format for tool parsing

-- Relationship 1: sales_transactions.product_id -> products.product_id
-- Relationship 2: sales_transactions.customer_id -> customers.customer_id  
-- Relationship 3: sales_transactions.store_id -> stores.store_id
-- Relationship 4: inventory_movements.product_id -> products.product_id

-- FOREIGN KEY DEFINITIONS

-- sales_transactions to products
ALTER TABLE sales_transactions ADD FOREIGN KEY (product_id) REFERENCES products(product_id);

-- sales_transactions to customers
ALTER TABLE sales_transactions ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- sales_transactions to stores  
ALTER TABLE sales_transactions ADD FOREIGN KEY (store_id) REFERENCES stores(store_id);

-- inventory_movements to products
ALTER TABLE inventory_movements ADD FOREIGN KEY (product_id) REFERENCES products(product_id);

-- RELATIONSHIP QUERIES

-- Query 1: Join sales with products
-- FROM sales_transactions JOIN products ON sales_transactions.product_id = products.product_id

-- Query 2: Join sales with customers
-- FROM sales_transactions JOIN customers ON sales_transactions.customer_id = customers.customer_id

-- Query 3: Join sales with stores
-- FROM sales_transactions JOIN stores ON sales_transactions.store_id = stores.store_id

-- Query 4: Join inventory with products
-- FROM inventory_movements JOIN products ON inventory_movements.product_id = products.product_id