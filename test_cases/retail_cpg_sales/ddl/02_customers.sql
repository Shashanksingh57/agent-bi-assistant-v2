-- Customers Master Table
-- This table contains customer information including type, segment, and region

CREATE TABLE customers (
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    account_manager VARCHAR(100),
    
    -- Constraints
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT chk_customer_type CHECK (customer_type IN ('Retailer', 'Distributor', 'Direct')),
    CONSTRAINT chk_segment CHECK (segment IN ('Large Chain', 'Independent', 'Online'))
);

-- Indexes for performance
CREATE INDEX idx_customers_type ON customers(customer_type);
CREATE INDEX idx_customers_segment ON customers(segment);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_customers_account_manager ON customers(account_manager);

-- Comments
COMMENT ON TABLE customers IS 'Customer master data';
COMMENT ON COLUMN customers.customer_id IS 'Unique customer identifier';
COMMENT ON COLUMN customers.customer_name IS 'Customer business name';
COMMENT ON COLUMN customers.customer_type IS 'Type of customer (Retailer, Distributor, Direct)';
COMMENT ON COLUMN customers.segment IS 'Customer segment (Large Chain, Independent, Online)';
COMMENT ON COLUMN customers.region IS 'Geographic region';
COMMENT ON COLUMN customers.account_manager IS 'Assigned account manager';