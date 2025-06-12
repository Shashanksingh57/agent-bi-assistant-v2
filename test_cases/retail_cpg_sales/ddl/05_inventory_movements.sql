-- Inventory Movements Table
-- This table tracks product movement and logistics data between locations

CREATE TABLE inventory_movements (
    movement_id VARCHAR(50) NOT NULL,
    movement_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    from_location VARCHAR(100) NOT NULL,
    to_location VARCHAR(100) NOT NULL,
    quantity_moved INTEGER NOT NULL,
    weight_tons DECIMAL(10,3) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    
    -- Constraints
    CONSTRAINT pk_inventory_movements PRIMARY KEY (movement_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_quantity_moved_positive CHECK (quantity_moved > 0),
    CONSTRAINT chk_weight_positive CHECK (weight_tons > 0),
    CONSTRAINT chk_movement_type CHECK (movement_type IN ('Inbound', 'Outbound', 'Transfer')),
    CONSTRAINT chk_different_locations CHECK (from_location != to_location)
);

-- Indexes for performance
CREATE INDEX idx_inventory_date ON inventory_movements(movement_date);
CREATE INDEX idx_inventory_product ON inventory_movements(product_id);
CREATE INDEX idx_inventory_from_location ON inventory_movements(from_location);
CREATE INDEX idx_inventory_to_location ON inventory_movements(to_location);
CREATE INDEX idx_inventory_movement_type ON inventory_movements(movement_type);
CREATE INDEX idx_inventory_date_product ON inventory_movements(movement_date, product_id);

-- Comments
COMMENT ON TABLE inventory_movements IS 'Product movement and logistics data';
COMMENT ON COLUMN inventory_movements.movement_id IS 'Unique movement identifier';
COMMENT ON COLUMN inventory_movements.movement_date IS 'Date of inventory movement';
COMMENT ON COLUMN inventory_movements.product_id IS 'Reference to product';
COMMENT ON COLUMN inventory_movements.from_location IS 'Origin location (warehouse/store)';
COMMENT ON COLUMN inventory_movements.to_location IS 'Destination location';
COMMENT ON COLUMN inventory_movements.quantity_moved IS 'Number of units moved';
COMMENT ON COLUMN inventory_movements.weight_tons IS 'Total weight moved in metric tons';
COMMENT ON COLUMN inventory_movements.movement_type IS 'Type of movement (Inbound, Outbound, Transfer)';