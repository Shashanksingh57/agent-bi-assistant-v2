-- =====================================================
-- Retail CPG Sales Database Relationships
-- Foreign Key Constraints Definition
-- Version: 1.0
-- =====================================================

-- This file defines all relationships between tables in the retail_cpg_sales schema
-- Execute this after all tables have been created

-- =====================================================
-- SALES_TRANSACTIONS RELATIONSHIPS
-- =====================================================

-- Sales Transaction -> Product (Many-to-One)
ALTER TABLE sales_transactions
ADD CONSTRAINT fk_sales_transactions_product
FOREIGN KEY (product_id) 
REFERENCES products(product_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Sales Transaction -> Customer (Many-to-One)
ALTER TABLE sales_transactions
ADD CONSTRAINT fk_sales_transactions_customer
FOREIGN KEY (customer_id) 
REFERENCES customers(customer_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Sales Transaction -> Store (Many-to-One)
ALTER TABLE sales_transactions
ADD CONSTRAINT fk_sales_transactions_store
FOREIGN KEY (store_id) 
REFERENCES stores(store_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- =====================================================
-- INVENTORY_MOVEMENTS RELATIONSHIPS
-- =====================================================

-- Inventory Movement -> Product (Many-to-One)
ALTER TABLE inventory_movements
ADD CONSTRAINT fk_inventory_movements_product
FOREIGN KEY (product_id) 
REFERENCES products(product_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- =====================================================
-- RELATIONSHIP SUMMARY
-- =====================================================
/*
Relationships Overview:
----------------------
1. sales_transactions.product_id -> products.product_id (Many-to-One)
   - Many sales transactions can reference one product
   
2. sales_transactions.customer_id -> customers.customer_id (Many-to-One)
   - Many sales transactions can be made by one customer
   
3. sales_transactions.store_id -> stores.store_id (Many-to-One)
   - Many sales transactions can occur at one store
   
4. inventory_movements.product_id -> products.product_id (Many-to-One)
   - Many inventory movements can involve one product

Cardinality Notes:
------------------
- products: Parent table for sales_transactions and inventory_movements
- customers: Parent table for sales_transactions
- stores: Parent table for sales_transactions
- sales_transactions: Child table with 3 foreign keys
- inventory_movements: Child table with 1 foreign key

Referential Integrity:
---------------------
- ON DELETE RESTRICT: Prevents deletion of parent records that have dependent children
- ON UPDATE CASCADE: Updates child records when parent key values change
*/