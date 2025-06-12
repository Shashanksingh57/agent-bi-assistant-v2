-- =====================================================
-- Retail CPG Sales Database Schema
-- Complete DDL Script
-- Version: 1.0
-- =====================================================

-- Create schema (if needed)
-- CREATE SCHEMA retail_cpg_sales;
-- USE retail_cpg_sales;

-- =====================================================
-- 1. PRODUCTS TABLE
-- =====================================================
CREATE TABLE products (
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    brand VARCHAR(100) NOT NULL,
    unit_weight_kg DECIMAL(8,3) NOT NULL,
    units_per_case INTEGER NOT NULL,
    list_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT chk_unit_weight_positive CHECK (unit_weight_kg > 0),
    CONSTRAINT chk_units_per_case_positive CHECK (units_per_case > 0),
    CONSTRAINT chk_list_price_positive CHECK (list_price > 0),
    CONSTRAINT chk_unit_cost_positive CHECK (unit_cost > 0)
);

-- =====================================================
-- 2. CUSTOMERS TABLE
-- =====================================================
CREATE TABLE customers (
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    account_manager VARCHAR(100),
    
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT chk_customer_type CHECK (customer_type IN ('Retailer', 'Distributor', 'Direct')),
    CONSTRAINT chk_segment CHECK (segment IN ('Large Chain', 'Independent', 'Online'))
);

-- =====================================================
-- 3. STORES TABLE
-- =====================================================
CREATE TABLE stores (
    store_id VARCHAR(50) NOT NULL,
    store_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    store_type VARCHAR(50) NOT NULL,
    store_size_sqft INTEGER,
    
    CONSTRAINT pk_stores PRIMARY KEY (store_id),
    CONSTRAINT chk_store_type CHECK (store_type IN ('Supermarket', 'Convenience', 'Warehouse')),
    CONSTRAINT chk_store_size_positive CHECK (store_size_sqft IS NULL OR store_size_sqft > 0)
);

-- =====================================================
-- 4. SALES TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE sales_transactions (
    transaction_id VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    quantity_sold INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_revenue DECIMAL(12,2) NOT NULL,
    cost_of_goods DECIMAL(12,2) NOT NULL,
    gross_profit DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    promotion_id VARCHAR(50),
    
    CONSTRAINT pk_sales_transactions PRIMARY KEY (transaction_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT chk_quantity_positive CHECK (quantity_sold > 0),
    CONSTRAINT chk_unit_price_positive CHECK (unit_price > 0),
    CONSTRAINT chk_total_revenue_positive CHECK (total_revenue >= 0),
    CONSTRAINT chk_cost_positive CHECK (cost_of_goods >= 0),
    CONSTRAINT chk_discount_non_negative CHECK (discount_amount >= 0)
);

-- =====================================================
-- 5. INVENTORY MOVEMENTS TABLE
-- =====================================================
CREATE TABLE inventory_movements (
    movement_id VARCHAR(50) NOT NULL,
    movement_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    from_location VARCHAR(100) NOT NULL,
    to_location VARCHAR(100) NOT NULL,
    quantity_moved INTEGER NOT NULL,
    weight_tons DECIMAL(10,3) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    
    CONSTRAINT pk_inventory_movements PRIMARY KEY (movement_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_quantity_moved_positive CHECK (quantity_moved > 0),
    CONSTRAINT chk_weight_positive CHECK (weight_tons > 0),
    CONSTRAINT chk_movement_type CHECK (movement_type IN ('Inbound', 'Outbound', 'Transfer')),
    CONSTRAINT chk_different_locations CHECK (from_location != to_location)
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Products indexes
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_category_subcategory ON products(category, subcategory);

-- Customers indexes
CREATE INDEX idx_customers_type ON customers(customer_type);
CREATE INDEX idx_customers_segment ON customers(segment);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_customers_account_manager ON customers(account_manager);

-- Stores indexes
CREATE INDEX idx_stores_city_state ON stores(city, state);
CREATE INDEX idx_stores_state ON stores(state);
CREATE INDEX idx_stores_country ON stores(country);
CREATE INDEX idx_stores_type ON stores(store_type);

-- Sales transactions indexes
CREATE INDEX idx_sales_date ON sales_transactions(transaction_date);
CREATE INDEX idx_sales_product ON sales_transactions(product_id);
CREATE INDEX idx_sales_customer ON sales_transactions(customer_id);
CREATE INDEX idx_sales_store ON sales_transactions(store_id);
CREATE INDEX idx_sales_date_product ON sales_transactions(transaction_date, product_id);
CREATE INDEX idx_sales_date_store ON sales_transactions(transaction_date, store_id);
CREATE INDEX idx_sales_promotion ON sales_transactions(promotion_id);

-- Inventory movements indexes
CREATE INDEX idx_inventory_date ON inventory_movements(movement_date);
CREATE INDEX idx_inventory_product ON inventory_movements(product_id);
CREATE INDEX idx_inventory_from_location ON inventory_movements(from_location);
CREATE INDEX idx_inventory_to_location ON inventory_movements(to_location);
CREATE INDEX idx_inventory_movement_type ON inventory_movements(movement_type);
CREATE INDEX idx_inventory_date_product ON inventory_movements(movement_date, product_id);

-- =====================================================
-- END OF SCHEMA
-- =====================================================