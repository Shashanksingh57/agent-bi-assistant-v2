# utils.py

from schemas import DashboardRequest
from typing import Dict, List, Any
import re

def build_prompt_from_payload(payload: DashboardRequest) -> str:
    """Build prompt for dashboard instruction generation"""
    prompt = f"You are a highly detailed dashboard assistant. Generate clear, beginner-friendly, step-by-step dashboard building instructions for {payload.platform} for the dashboard titled '{payload.dashboard_name}'.\n"
    prompt += "You must cover each visual requested, mentioning type, field, aggregation, formatting, filters, and customizations.\n"
    prompt += "Instructions must be detailed, even if the data fields are simple.\n\n"

    for idx, visual in enumerate(payload.visuals, 1):
        prompt += f"Visual {idx}:\n"
        prompt += f"- Visual Type: {visual.visual_type}\n"
        prompt += f"- Title: {visual.title}\n"
        if visual.field:
            prompt += f"- Field: {visual.field}\n"
        if visual.aggregation:
            prompt += f"- Aggregation: {visual.aggregation}\n"
        if visual.formatting:
            prompt += f"- Formatting: {visual.formatting.type}, Currency symbol: {visual.formatting.currency_symbol}, Decimals: {visual.formatting.decimal_places}\n"
        if visual.filters:
            for filt in visual.filters:
                prompt += f"- Filter: {filt.field} where {filt.condition}\n"
        if visual.custom_colors:
            prompt += f"- Custom colors: Text {visual.custom_colors.text_color}, Background {visual.custom_colors.background_color}\n"
        if visual.tooltip_customization and visual.tooltip_customization.enable:
            prompt += f"- Tooltips: {', '.join(visual.tooltip_customization.fields)}\n"

    prompt += "\nReturn a numbered list of clean dashboard assembly instructions."
    return prompt

def build_data_prep_prompt(platform: str, model_metadata: dict, custom_requirements: str = "") -> str:
    """
    Build a comprehensive prompt for data preparation that includes specific column analysis
    """
    if not model_metadata:
        return "No data model provided. Please define your data model first."
    
    tables = model_metadata.get("tables", [])
    relationships = model_metadata.get("relationships", [])
    
    prompt = f"""You are an expert {platform} data preparation specialist. Generate detailed, step-by-step data preparation instructions based on the following data model analysis:

## Data Model Overview:
- Total Tables: {len(tables)}
- Total Relationships: {len(relationships)}

## Detailed Table Analysis:
"""
    
    for table in tables:
        table_name = table.get("name", "Unknown")
        columns = table.get("columns", [])
        
        prompt += f"\n### Table: {table_name}\n"
        prompt += f"Columns ({len(columns)} total):\n"
        
        # Categorize columns
        date_columns = []
        numeric_columns = []
        text_columns = []
        nullable_columns = []
        primary_keys = []
        foreign_keys = []
        potential_issues = []
        
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "").lower()
            is_nullable = col.get("nullable", True)
            is_primary_key = col.get("is_primary_key", False)
            is_foreign_key = col.get("is_foreign_key", False)
            
            # Categorize
            if is_primary_key:
                primary_keys.append(f"{col_name} ({col_type})")
            if is_foreign_key:
                foreign_keys.append(f"{col_name} ({col_type})")
            if "date" in col_type or "time" in col_type or "timestamp" in col_type:
                date_columns.append(f"{col_name} ({col_type})")
            elif any(t in col_type for t in ["int", "float", "decimal", "numeric", "money", "currency"]):
                numeric_columns.append(f"{col_name} ({col_type})")
            elif any(t in col_type for t in ["varchar", "char", "text", "string", "nvarchar"]):
                text_columns.append(f"{col_name} ({col_type})")
            
            if is_nullable:
                nullable_columns.append(f"{col_name}")
            
            # Identify potential issues
            if "id" in col_name.lower() and is_nullable:
                potential_issues.append(f"ID column '{col_name}' allows nulls")
            
            if any(word in col_name.lower() for word in ["amount", "price", "cost", "salary"]) and "varchar" in col_type:
                potential_issues.append(f"Monetary column '{col_name}' stored as text")
            
            if "date" in col_name.lower() and "varchar" in col_type:
                potential_issues.append(f"Date column '{col_name}' stored as text")
        
        # Add categorized information to prompt
        if primary_keys:
            prompt += f"- Primary Keys: {', '.join(primary_keys)}\n"
        if foreign_keys:
            prompt += f"- Foreign Keys: {', '.join(foreign_keys)}\n"
        if date_columns:
            prompt += f"- Date/Time Columns: {', '.join(date_columns)}\n"
        if numeric_columns:
            prompt += f"- Numeric Columns: {', '.join(numeric_columns)}\n"
        if text_columns:
            prompt += f"- Text Columns: {', '.join(text_columns)}\n"
        if nullable_columns:
            prompt += f"- Nullable Columns: {', '.join(nullable_columns)}\n"
        if potential_issues:
            prompt += f"- ⚠️ Data Quality Issues: {'; '.join(potential_issues)}\n"
    
    # Add relationships
    if relationships:
        prompt += f"\n## Relationships:\n"
        for rel in relationships:
            from_table = rel.get("from", "")
            to_table = rel.get("to", "")
            rel_type = rel.get("type", "")
            from_col = rel.get("from_column", "")
            to_col = rel.get("to_column", "")
            prompt += f"- {from_table}.{from_col} → {to_table}.{to_col} ({rel_type})\n"
    
    # Add custom requirements
    if custom_requirements.strip():
        prompt += f"\n## Additional Requirements:\n{custom_requirements}\n"
    
    # Platform-specific instructions
    if platform.lower() == "power bi":
        prompt += f"""
## Generate Power BI Power Query M Instructions:

For each table, provide SPECIFIC instructions including:

1. **Data Source Connection:**
   - Exact steps to connect to the data source
   - Authentication requirements

2. **Column-Specific Transformations:**
   - For EACH date column: specific date parsing and format correction steps with M code
   - For EACH numeric column: data type conversion, currency symbol removal, decimal handling with M code
   - For EACH text column: trimming, case standardization, encoding issues with M code

3. **Data Quality Fixes:**
   - For EACH nullable column: specific null handling strategy with business justification
   - Duplicate detection based on primary keys with M code
   - Address each potential issue identified above with specific solutions

4. **Performance Optimization:**
   - Query folding considerations
   - Indexing recommendations
   - Memory optimization tips

5. **Relationship Setup:**
   - Exact relationship configuration steps
   - Cross-filter direction recommendations

Provide numbered steps with exact Power Query M code snippets for each transformation.
Include validation steps to verify data quality after each major transformation.
"""
    
    elif platform.lower() == "tableau":
        prompt += f"""
## Generate Tableau Prep/Desktop Instructions:

For each table, provide SPECIFIC instructions including:

1. **Data Connection:**
   - Connection type and parameters
   - Join configurations

2. **Column-Specific Cleaning:**
   - For EACH date column: parsing, format standardization in Tableau
   - For EACH numeric column: type conversion, null handling
   - For EACH text column: cleaning, standardization

3. **Data Modeling:**
   - Relationship setup in Tableau Desktop
   - Calculated field recommendations

4. **Performance Optimization:**
   - Extract vs Live connection recommendations
   - Performance optimization tips

Provide step-by-step instructions with Tableau-specific terminology and calculated field syntax.
"""
    
    else:
        prompt += f"""
## Generate Generic Data Preparation Instructions:

Provide platform-agnostic instructions that cover:
1. Data loading and connection
2. Column-specific transformations for each identified issue
3. Data quality assurance
4. Relationship establishment
5. Performance considerations

Focus on the logical steps that can be adapted to any BI platform.
"""
    
    prompt += f"""
## Output Requirements:
- Use clear markdown formatting with headers and numbered lists
- Reference SPECIFIC column names from the data model above
- Include code snippets or platform-specific syntax where applicable
- Provide validation steps to verify data quality
- Include troubleshooting tips for common issues
- Estimate time for each major step
- Address each potential issue identified in the analysis
- Include business impact of data quality issues if not addressed
"""
    
    return prompt

def extract_column_metadata(table_data: dict) -> dict:
    """
    Extract detailed metadata about columns for better preparation instructions
    """
    columns = table_data.get("columns", [])
    metadata = {
        "total_columns": len(columns),
        "by_type": {},
        "nullable_count": 0,
        "key_columns": [],
        "potential_issues": []
    }
    
    for col in columns:
        col_type = col.get("type", "unknown").lower()
        is_nullable = col.get("nullable", True)
        col_name = col.get("name", "")
        
        # Count by type
        if col_type not in metadata["by_type"]:
            metadata["by_type"][col_type] = 0
        metadata["by_type"][col_type] += 1
        
        # Count nullables
        if is_nullable:
            metadata["nullable_count"] += 1
        
        # Identify key columns
        if col.get("is_primary_key") or col.get("is_foreign_key"):
            metadata["key_columns"].append(col_name)
        
        # Flag potential issues
        if "id" in col_name.lower() and is_nullable:
            metadata["potential_issues"].append(f"ID column '{col_name}' is nullable")
        
        if any(word in col_name.lower() for word in ["amount", "price", "cost"]) and "varchar" in col_type:
            metadata["potential_issues"].append(f"Monetary column '{col_name}' stored as text")
    
    return metadata

def generate_platform_specific_instructions(platform: str, analysis: Dict[str, Any]) -> str:
    """
    Generate platform-specific data preparation instructions
    """
    if platform.lower() == "power bi":
        return generate_powerbi_instructions(analysis)
    elif platform.lower() == "tableau":
        return generate_tableau_instructions(analysis)
    else:
        return generate_generic_instructions(analysis)

def generate_powerbi_instructions(analysis: Dict[str, Any]) -> str:
    """
    Generate Power BI specific Power Query M instructions
    """
    instructions = []
    instructions.append("# Power BI Data Preparation Steps")
    instructions.append("## 1. Data Source Connection")
    
    for table in analysis["tables"]:
        table_name = table["name"]
        instructions.append(f"\n### Table: {table_name}")
        
        # Data Loading
        instructions.append(f"1. **Load {table_name} table:**")
        instructions.append(f"   - Go to Home > Get Data > Choose your data source")
        instructions.append(f"   - Select table '{table_name}'")
        instructions.append(f"   - Click 'Transform Data' to open Power Query Editor")
        
        # Data Type Corrections
        instructions.append(f"\n2. **Data Type Corrections for {table_name}:**")
        
        # Date columns
        if table["date_columns"]:
            instructions.append("   **Date Columns:**")
            for col in table["date_columns"]:
                instructions.append(f"   - Right-click '{col}' column > Change Type > Date/Time")
                instructions.append(f"   - Verify date format is consistent")
        
        # Numeric columns
        if table["numeric_columns"]:
            instructions.append("   **Numeric Columns:**")
            for col in table["numeric_columns"]:
                instructions.append(f"   - Right-click '{col}' column > Change Type > Decimal Number")
                instructions.append(f"   - Check for currency symbols or formatting issues")
        
        # Text columns
        if table["text_columns"]:
            instructions.append("   **Text Columns:**")
            for col in table["text_columns"]:
                instructions.append(f"   - Right-click '{col}' column > Change Type > Text")
                instructions.append(f"   - Trim whitespace: Transform > Trim")
        
        # Null Handling
        if table["nullable_columns"]:
            instructions.append(f"\n3. **Null Value Handling for {table_name}:**")
            for col in table["nullable_columns"]:
                col_type = next((c["type"] for c in table["columns"] if c["name"] == col), "text")
                if "numeric" in col_type or "int" in col_type or "decimal" in col_type:
                    instructions.append(f"   - '{col}': Replace null values with 0 or use Replace Values")
                elif "date" in col_type:
                    instructions.append(f"   - '{col}': Consider replacing null dates with default date or remove rows")
                else:
                    instructions.append(f"   - '{col}': Replace null values with 'Unknown' or empty string")
        
        # Duplicate Handling
        instructions.append(f"\n4. **Duplicate Handling for {table_name}:**")
        if table["primary_keys"]:
            pk_cols = ", ".join(table["primary_keys"])
            instructions.append(f"   - Remove duplicates based on primary key(s): {pk_cols}")
            instructions.append(f"   - Select columns: {pk_cols} > Remove Rows > Remove Duplicates")
        else:
            instructions.append(f"   - Remove duplicates based on all columns")
            instructions.append(f"   - Home > Remove Rows > Remove Duplicates")
        
        # Data Validation
        instructions.append(f"\n5. **Data Validation for {table_name}:**")
        instructions.append(f"   - Check column quality: View > Column Quality")
        instructions.append(f"   - Review data distribution: View > Column Distribution")
        instructions.append(f"   - Check for unexpected values in key columns")
    
    # Relationships
    if analysis["relationships"]:
        instructions.append(f"\n## 2. Relationships Setup")
        instructions.append("After loading all tables, set up relationships in Model view:")
        
        for rel in analysis["relationships"]:
            instructions.append(f"\n**{rel['from_table']} → {rel['to_table']}:**")
            instructions.append(f"   - Relationship type: {rel['type']}")
            instructions.append(f"   - From: {rel['from_table']}.{rel.get('from_column', '')}")
            instructions.append(f"   - To: {rel['to_table']}.{rel.get('to_column', '')}")
            instructions.append(f"   - Cross filter direction: Both (if needed for analysis)")
    
    # Final steps
    instructions.append(f"\n## 3. Final Steps")
    instructions.append("1. **Apply Changes:** Click 'Close & Apply' in Power Query Editor")
    instructions.append("2. **Verify Data:** Check row counts and sample data in each table")
    instructions.append("3. **Create Measures:** Go to Model view and create necessary calculated measures")
    instructions.append("4. **Optimize Performance:** Consider creating aggregation tables if needed")
    
    return "\n".join(instructions)

def generate_tableau_instructions(analysis: Dict[str, Any]) -> str:
    """
    Generate Tableau specific data preparation instructions
    """
    instructions = []
    instructions.append("# Tableau Data Preparation Steps")
    instructions.append("## 1. Data Connection and Tableau Prep")
    
    for table in analysis["tables"]:
        table_name = table["name"]
        instructions.append(f"\n### Table: {table_name}")
        
        instructions.append(f"1. **Connect to {table_name}:**")
        instructions.append(f"   - Open Tableau Prep Builder")
        instructions.append(f"   - Connect to your data source")
        instructions.append(f"   - Select table '{table_name}'")
        
        # Data Cleaning
        instructions.append(f"\n2. **Data Cleaning for {table_name}:**")
        
        # Date columns
        if table["date_columns"]:
            for col in table["date_columns"]:
                instructions.append(f"   - **{col}**: Change data type to Date/DateTime")
                instructions.append(f"   - Verify date parsing is correct")
        
        # Numeric columns
        if table["numeric_columns"]:
            for col in table["numeric_columns"]:
                instructions.append(f"   - **{col}**: Change data type to Number")
                instructions.append(f"   - Clean any currency symbols or text")
        
        # Null handling
        if table["nullable_columns"]:
            instructions.append(f"\n3. **Null Value Treatment:**")
            for col in table["nullable_columns"]:
                instructions.append(f"   - **{col}**: Use Clean step to handle nulls")
                instructions.append(f"   - Consider replacing with appropriate default values")
    
    # Relationships in Tableau
    if analysis["relationships"]:
        instructions.append(f"\n## 2. Data Model Setup")
        instructions.append("Set up relationships in Tableau Desktop:")
        
        for rel in analysis["relationships"]:
            instructions.append(f"\n**Join {rel['from_table']} with {rel['to_table']}:**")
            instructions.append(f"   - Join type: {rel['type']}")
            instructions.append(f"   - Join fields: {rel.get('from_column', '')} = {rel.get('to_column', '')}")
    
    return "\n".join(instructions)

def generate_generic_instructions(analysis: Dict[str, Any]) -> str:
    """
    Generate generic data preparation instructions
    """
    instructions = []
    instructions.append("# Generic Data Preparation Steps")
    
    for table in analysis["tables"]:
        table_name = table["name"]
        instructions.append(f"\n## Table: {table_name}")
        
        if table["date_columns"]:
            instructions.append(f"**Date Columns:** {', '.join(table['date_columns'])}")
            instructions.append("- Ensure consistent date format")
            instructions.append("- Handle null dates appropriately")
        
        if table["numeric_columns"]:
            instructions.append(f"**Numeric Columns:** {', '.join(table['numeric_columns'])}")
            instructions.append("- Remove currency symbols and formatting")
            instructions.append("- Handle null values (replace with 0 or remove rows)")
        
        if table["text_columns"]:
            instructions.append(f"**Text Columns:** {', '.join(table['text_columns'])}")
            instructions.append("- Trim whitespace")
            instructions.append("- Standardize text casing if needed")
    
    return "\n".join(instructions)

def tidy_md(md: str) -> str:
    """Clean up markdown formatting for better display"""
    # Blank line after any ## heading
    md = re.sub(r'(?m)^(## .+)', r'\1\n', md)
    # Start numbered lists on a new line
    md = re.sub(r'(?m)^(\d+\.)', r'\n\1', md)
    # Indent any dash bullets
    md = re.sub(r'(?m)^\s*-\s+', r'  - ', md)
    return md.strip()

def validate_data_model(model_metadata: dict) -> dict:
    """
    Validate data model and return validation results
    """
    validation_results = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "suggestions": []
    }
    
    if not model_metadata:
        validation_results["is_valid"] = False
        validation_results["errors"].append("No data model provided")
        return validation_results
    
    tables = model_metadata.get("tables", [])
    relationships = model_metadata.get("relationships", [])
    
    # Check for tables without primary keys
    for table in tables:
        table_name = table.get("name", "")
        columns = table.get("columns", [])
        
        has_primary_key = any(col.get("is_primary_key") for col in columns)
        if not has_primary_key:
            validation_results["warnings"].append(f"Table '{table_name}' has no primary key defined")
        
        # Check for ID columns that are nullable
        for col in columns:
            col_name = col.get("name", "")
            if "id" in col_name.lower() and col.get("nullable", True):
                validation_results["warnings"].append(f"ID column '{table_name}.{col_name}' allows nulls")
    
    # Check for orphaned relationships
    table_names = [table.get("name", "") for table in tables]
    for rel in relationships:
        from_table = rel.get("from", "")
        to_table = rel.get("to", "")
        
        if from_table not in table_names:
            validation_results["errors"].append(f"Relationship references non-existent table: {from_table}")
        if to_table not in table_names:
            validation_results["errors"].append(f"Relationship references non-existent table: {to_table}")
    
    if validation_results["errors"]:
        validation_results["is_valid"] = False
    
    return validation_results