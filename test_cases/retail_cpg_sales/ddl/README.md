# Retail CPG Sales Database DDL Scripts

This folder contains SQL Data Definition Language (DDL) scripts for creating the Retail CPG Sales database schema.

## Files Overview

### Complete Schema
- **`00_retail_cpg_complete_schema.sql`** - Complete schema with all tables in the correct order

### Individual Table Scripts
1. **`01_products.sql`** - Products master table
2. **`02_customers.sql`** - Customers master table
3. **`03_stores.sql`** - Stores location table
4. **`04_sales_transactions.sql`** - Sales transactions fact table
5. **`05_inventory_movements.sql`** - Inventory movements tracking table
6. **`06_relationships.sql`** - Foreign key relationships between tables

### Relationship Files
- **`relationships_simple.txt`** - Simple format for tool: Table1(Column) = Table2(Column)
- **`relationships.txt`** - Detailed relationship definitions with examples
- **`relationships_simple.sql`** - Simplified SQL format
- **`relationships.json`** - Machine-readable relationship definitions (if tool supports JSON)

## Schema Overview

### Tables
- **products** - Product catalog with pricing and specifications
- **customers** - Customer information with segmentation
- **stores** - Store locations and characteristics
- **sales_transactions** - Daily sales transaction records (fact table)
- **inventory_movements** - Product movement between locations

### Key Relationships
- `sales_transactions.product_id` → `products.product_id`
- `sales_transactions.customer_id` → `customers.customer_id`
- `sales_transactions.store_id` → `stores.store_id`
- `inventory_movements.product_id` → `products.product_id`

## Usage

### Option 1: Execute Complete Schema
```sql
-- Run the complete schema file
SOURCE 00_retail_cpg_complete_schema.sql;
```

### Option 2: Execute Individual Tables
```sql
-- Execute in order due to foreign key constraints
SOURCE 01_products.sql;
SOURCE 02_customers.sql;
SOURCE 03_stores.sql;
SOURCE 04_sales_transactions.sql;
SOURCE 05_inventory_movements.sql;
```

## Database Compatibility

These DDL scripts are written in standard SQL and should work with most relational databases including:
- PostgreSQL
- MySQL (may need minor syntax adjustments for CHECK constraints)
- SQL Server
- Oracle (may need VARCHAR2 instead of VARCHAR)

## Notes

1. **Primary Keys**: All tables have single-column primary keys
2. **Foreign Keys**: Referential integrity is enforced through foreign key constraints
3. **Check Constraints**: Business rules are enforced through CHECK constraints
4. **Indexes**: Performance indexes are created on commonly queried columns
5. **Data Types**: Uses standard SQL data types; adjust as needed for your specific database

## Sample Data

For sample data to populate these tables, refer to the parent directory's test case files.