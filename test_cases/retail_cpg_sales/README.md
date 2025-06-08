# Retail/CPG Sales Dashboard Test Cases

This directory contains comprehensive test cases for the AI-powered BI Dashboard Assistant, specifically designed for a retail/CPG company sales team tracking revenue, profit, and tonnage metrics.

## Test Case Contents

### 1. **data_model.json**
- Complete JSON schema for a retail/CPG sales data model
- 5 interconnected tables: sales_transactions, products, customers, stores, inventory_movements
- Includes relationships and foreign key constraints
- Covers all fields needed for revenue, profit, and tonnage tracking

### 2. **kpis.json**
- 10 key performance indicators relevant to retail/CPG sales
- Primary KPIs: Total Revenue, Gross Profit, Total Tons Moved
- Supporting metrics: Revenue per Ton, Units Sold, Average Order Value, etc.
- Each KPI includes calculation logic, aggregation levels, and typical targets

### 3. **data_dictionary.csv**
- Comprehensive field-level documentation
- Business definitions and rules for each data element
- Example values and validation rules
- Critical for understanding data semantics

### 4. **wireframe_description.txt**
- Detailed text description of a sales dashboard layout
- 4-row grid layout with KPI cards, trend charts, and analytics
- Describes interactive features and visual elements
- Can be used to test text-based wireframe processing

### 5. **api_test_scenarios.json**
- 10 test scenarios covering all API endpoints
- Includes positive tests, error handling, and edge cases
- End-to-end workflow test
- Performance benchmarks for each endpoint

## How to Use These Test Cases

### For Manual Testing:
1. Start the application: `cd agent-bi-assistant && python run.py`
2. Use the Streamlit UI to upload the data model and wireframe description
3. Select target BI platform (Tableau, PowerBI, etc.)
4. Verify generated instructions match expected outputs

### For API Testing:
```bash
# Example: Test model generation
curl -X POST http://localhost:8000/api/v1/generate-model \
  -H "Authorization: Bearer supersecrettoken123" \
  -H "Content-Type: application/json" \
  -d @test_cases/retail_cpg_sales/data_model.json

# Example: Test layout generation
curl -X POST http://localhost:8000/api/v1/generate-layout \
  -H "Authorization: Bearer supersecrettoken123" \
  -H "Content-Type: application/json" \
  -d '{
    "data_model": <contents of data_model.json>,
    "kpis": <contents of kpis.json>,
    "wireframe_description": <contents of wireframe_description.txt>,
    "target_platform": "Tableau"
  }'
```

### Test Coverage Areas:
- **Data Model Processing**: SQL DDL to JSON conversion
- **KPI Definition**: Business metric calculations
- **Wireframe Analysis**: Text and image-based layout extraction
- **Platform-Specific Output**: Tableau, PowerBI, Looker, QuickSight
- **Sprint Planning**: Agile story generation
- **Error Handling**: Authentication, validation, edge cases

## Expected Outcomes

When using these test cases, the system should:
1. Successfully parse and understand the retail/CPG data model
2. Generate appropriate data preparation instructions for the chosen BI platform
3. Create detailed dashboard implementation instructions based on the wireframe
4. Include specific guidance for implementing revenue, profit, and tonnage KPIs
5. Provide sprint-ready user stories for development teams

## Notes
- The data model represents a typical retail/CPG company structure
- KPIs focus on sales team needs: revenue performance, profitability, and logistics efficiency
- The wireframe emphasizes executive-level overview with drill-down capabilities
- Test scenarios cover both happy path and error conditions