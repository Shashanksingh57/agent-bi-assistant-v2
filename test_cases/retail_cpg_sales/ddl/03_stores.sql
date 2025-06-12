-- Stores Master Table
-- This table contains store location and characteristics data

CREATE TABLE stores (
    store_id VARCHAR(50) NOT NULL,
    store_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    store_type VARCHAR(50) NOT NULL,
    store_size_sqft INTEGER,
    
    -- Constraints
    CONSTRAINT pk_stores PRIMARY KEY (store_id),
    CONSTRAINT chk_store_type CHECK (store_type IN ('Supermarket', 'Convenience', 'Warehouse')),
    CONSTRAINT chk_store_size_positive CHECK (store_size_sqft IS NULL OR store_size_sqft > 0)
);

-- Indexes for performance
CREATE INDEX idx_stores_city_state ON stores(city, state);
CREATE INDEX idx_stores_state ON stores(state);
CREATE INDEX idx_stores_country ON stores(country);
CREATE INDEX idx_stores_type ON stores(store_type);

-- Comments
COMMENT ON TABLE stores IS 'Store location data';
COMMENT ON COLUMN stores.store_id IS 'Unique store identifier';
COMMENT ON COLUMN stores.store_name IS 'Store name';
COMMENT ON COLUMN stores.city IS 'Store city';
COMMENT ON COLUMN stores.state IS 'Store state/province';
COMMENT ON COLUMN stores.country IS 'Store country';
COMMENT ON COLUMN stores.store_type IS 'Type of store (Supermarket, Convenience, Warehouse)';
COMMENT ON COLUMN stores.store_size_sqft IS 'Store size in square feet';