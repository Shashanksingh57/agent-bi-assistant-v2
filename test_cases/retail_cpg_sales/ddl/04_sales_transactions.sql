-- Sales Transactions Table
-- This table contains daily sales transaction data with foreign keys to products, customers, and stores

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
    
    -- Constraints
    CONSTRAINT pk_sales_transactions PRIMARY KEY (transaction_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT chk_quantity_positive CHECK (quantity_sold > 0),
    CONSTRAINT chk_unit_price_positive CHECK (unit_price > 0),
    CONSTRAINT chk_total_revenue_positive CHECK (total_revenue >= 0),
    CONSTRAINT chk_cost_positive CHECK (cost_of_goods >= 0),
    CONSTRAINT chk_discount_non_negative CHECK (discount_amount >= 0),
    CONSTRAINT chk_revenue_calculation CHECK (total_revenue = (quantity_sold * unit_price) - discount_amount),
    CONSTRAINT chk_profit_calculation CHECK (gross_profit = total_revenue - cost_of_goods)
);

-- Indexes for performance
CREATE INDEX idx_sales_date ON sales_transactions(transaction_date);
CREATE INDEX idx_sales_product ON sales_transactions(product_id);
CREATE INDEX idx_sales_customer ON sales_transactions(customer_id);
CREATE INDEX idx_sales_store ON sales_transactions(store_id);
CREATE INDEX idx_sales_date_product ON sales_transactions(transaction_date, product_id);
CREATE INDEX idx_sales_date_store ON sales_transactions(transaction_date, store_id);
CREATE INDEX idx_sales_promotion ON sales_transactions(promotion_id);

-- Comments
COMMENT ON TABLE sales_transactions IS 'Daily sales transaction data';
COMMENT ON COLUMN sales_transactions.transaction_id IS 'Unique identifier for each transaction';
COMMENT ON COLUMN sales_transactions.transaction_date IS 'Date of the sales transaction';
COMMENT ON COLUMN sales_transactions.product_id IS 'Reference to product sold';
COMMENT ON COLUMN sales_transactions.customer_id IS 'Reference to customer';
COMMENT ON COLUMN sales_transactions.store_id IS 'Reference to store location';
COMMENT ON COLUMN sales_transactions.quantity_sold IS 'Number of units sold';
COMMENT ON COLUMN sales_transactions.unit_price IS 'Price per unit at time of sale';
COMMENT ON COLUMN sales_transactions.total_revenue IS 'Total revenue for the transaction';
COMMENT ON COLUMN sales_transactions.cost_of_goods IS 'Total cost of goods sold';
COMMENT ON COLUMN sales_transactions.gross_profit IS 'Gross profit (revenue - cost)';
COMMENT ON COLUMN sales_transactions.discount_amount IS 'Discount applied to transaction';
COMMENT ON COLUMN sales_transactions.promotion_id IS 'Reference to active promotion';