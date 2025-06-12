-- Products Master Table
-- This table contains the product catalog with all product details

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
    
    -- Constraints
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT chk_unit_weight_positive CHECK (unit_weight_kg > 0),
    CONSTRAINT chk_units_per_case_positive CHECK (units_per_case > 0),
    CONSTRAINT chk_list_price_positive CHECK (list_price > 0),
    CONSTRAINT chk_unit_cost_positive CHECK (unit_cost > 0)
);

-- Indexes for performance
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_category_subcategory ON products(category, subcategory);

-- Comments
COMMENT ON TABLE products IS 'Product master data containing all product information';
COMMENT ON COLUMN products.product_id IS 'Unique product identifier';
COMMENT ON COLUMN products.product_name IS 'Product name';
COMMENT ON COLUMN products.category IS 'Product category';
COMMENT ON COLUMN products.subcategory IS 'Product subcategory';
COMMENT ON COLUMN products.brand IS 'Product brand';
COMMENT ON COLUMN products.unit_weight_kg IS 'Weight per unit in kilograms';
COMMENT ON COLUMN products.units_per_case IS 'Number of units per case';
COMMENT ON COLUMN products.list_price IS 'Standard list price';
COMMENT ON COLUMN products.unit_cost IS 'Cost per unit';