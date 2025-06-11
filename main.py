# main.py - Enhanced with AI Vision, OCR/Tesseract removed

import os
import io
import json
import re
import base64
import numpy as np
import cv2
import logging
import time

from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from PIL import Image

# ─── Configuration ───────────────────────────────────────────────────────────────
load_dotenv()

# Initialize OpenAI client for v1.0+ with very generous timeout settings
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=900.0,  # 15 minutes global timeout (was working before)
    max_retries=2   # Fewer retries but longer timeouts
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic BI Assistant")


# ─── Helper Functions ────────────────────────────────────────────────────────────
def safe_get_dict(obj, default=None):
    """Safely get dictionary from object, handling string/None cases"""
    if obj is None:
        return default or {}
    if isinstance(obj, str):
        try:
            import json
            return json.loads(obj)
        except (json.JSONDecodeError, ValueError):
            return default or {}
    if isinstance(obj, dict):
        return obj
    return default or {}

def safe_get_list(obj, default=None):
    """Safely get list from object"""
    if obj is None:
        return default or []
    if isinstance(obj, str):
        try:
            import json
            parsed = json.loads(obj)
            return parsed if isinstance(parsed, list) else default or []
        except (json.JSONDecodeError, ValueError):
            return default or []
    if isinstance(obj, list):
        return obj
    return default or []

def create_optimized_openai_call(messages, max_tokens=2000, timeout=600):
    """Create OpenAI API call with timeout and error handling"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens,
            timeout=timeout
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(500, f"AI service error: {str(e)}")

def create_vision_call_with_retry(messages, max_tokens=2000, timeout=900, max_retries=2):
    """Create GPT-4o Vision API call with retry logic for better reliability"""
    import time
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                wait_time = 10 + (attempt * 10)  # 10, 20 seconds wait
                logger.info(f"Retrying vision API call in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(wait_time)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Latest and fastest vision model
                messages=messages,
                temperature=0.1,
                max_tokens=max_tokens,
                timeout=timeout,
                # Add performance optimizations
                stream=False  # Ensure we get the full response at once
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Vision API attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries:  # Last attempt
                raise HTTPException(500, f"Vision AI service failed after {max_retries + 1} attempts: {str(e)}")
            continue

# ─── Schemas ─────────────────────────────────────────────────────────────────────
class Section(BaseModel):
    layout_type: str
    section:     str
    label:       str

class GenerateRequest(BaseModel):
    sketch_description: str
    platform_selected:  str
    custom_prompt:      Optional[str]           = ""
    model_metadata:     Optional[Dict[str,Any]] = None
    include_data_prep:  bool                    = False
    data_prep_only:     bool                    = False
    kpi_list:           Optional[List[Dict[str,str]]] = None
    data_dictionary:    Optional[Dict[str,Dict[str,Dict[str,str]]]] = None
    instruction_complexity: Optional[str]       = "intermediate"  # beginner, intermediate, expert

class GenerateResponse(BaseModel):
    wireframe_json:      Any   # can be str or object
    layout_instructions: str

class ModelGenRequest(BaseModel):
    tables_sql:        List[str]
    relationships_sql: str

class ModelGenResponse(BaseModel):
    data_model: Dict[str, Any]

class SprintRequest(BaseModel):
    wireframe_json:      Dict[str, Any]
    layout_instructions: str
    sprint_length_days:  int
    velocity:            int

class SprintResponse(BaseModel):
    sprint_stories:       List[Dict[str, Any]]
    over_under_capacity:  int

# ─── Data Prep Analysis Functions ───────────────────────────────────────────────
def analyze_data_model_for_prep(model_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the data model to identify specific data preparation requirements"""
    analysis = {
        "tables": [],
        "relationships": [],
        "data_quality_issues": [],
        "transformation_needs": []
    }
    
    if not model_metadata:
        return analysis
    
    # FIXED: Safely parse model_metadata
    model_dict = safe_get_dict(model_metadata)
    if not model_dict:
        logger.warning("Could not parse model_metadata as dictionary")
        return analysis
    
    tables = safe_get_list(model_dict.get("tables", []))
    relationships = safe_get_list(model_dict.get("relationships", []))
    
    logger.info(f"Processing {len(tables)} tables and {len(relationships)} relationships")
    
    for table in tables:
        # Ensure table is a dictionary
        table_dict = safe_get_dict(table)
        if not table_dict:
            logger.warning(f"Skipping invalid table: {table}")
            continue
            
        table_name = table_dict.get("name", "Unknown")
        columns = safe_get_list(table_dict.get("columns", []))
        
        logger.info(f"Processing table '{table_name}' with {len(columns)} columns")
        
        table_analysis = {
            "name": table_name,
            "columns": [],
            "primary_keys": [],
            "foreign_keys": [],
            "date_columns": [],
            "numeric_columns": [],
            "text_columns": [],
            "nullable_columns": [],
            "potential_issues": []
        }
        
        for col in columns:
            # Ensure column is a dictionary
            col_dict = safe_get_dict(col)
            if not col_dict:
                logger.warning(f"Skipping invalid column: {col}")
                continue
                
            col_name = col_dict.get("name", "")
            col_type = str(col_dict.get("type", "")).lower()
            is_nullable = col_dict.get("nullable", True)
            is_primary_key = col_dict.get("is_primary_key", False)
            is_foreign_key = col_dict.get("is_foreign_key", False)
            
            column_info = {
                "name": col_name,
                "type": col_type,
                "nullable": is_nullable,
                "is_primary_key": is_primary_key,
                "is_foreign_key": is_foreign_key
            }
            
            table_analysis["columns"].append(column_info)
            
            # Categorize columns
            if is_primary_key:
                table_analysis["primary_keys"].append(col_name)
            if is_foreign_key:
                table_analysis["foreign_keys"].append(col_name)
            
            if "date" in col_type or "time" in col_type or "timestamp" in col_type:
                table_analysis["date_columns"].append(col_name)
            elif any(t in col_type for t in ["int", "float", "decimal", "numeric", "money", "currency"]):
                table_analysis["numeric_columns"].append(col_name)
            elif any(t in col_type for t in ["varchar", "char", "text", "string", "nvarchar"]):
                table_analysis["text_columns"].append(col_name)
            
            if is_nullable:
                table_analysis["nullable_columns"].append(col_name)
            
            # Identify potential issues
            if "id" in col_name.lower() and is_nullable:
                table_analysis["potential_issues"].append(f"ID column '{col_name}' allows nulls")
            
            if any(word in col_name.lower() for word in ["amount", "price", "cost", "salary"]) and "varchar" in col_type:
                table_analysis["potential_issues"].append(f"Monetary column '{col_name}' stored as text")
            
            if "date" in col_name.lower() and "varchar" in col_type:
                table_analysis["potential_issues"].append(f"Date column '{col_name}' stored as text")
        
        analysis["tables"].append(table_analysis)
    
    # Analyze relationships
    for rel in relationships:
        rel_dict = safe_get_dict(rel)
        if not rel_dict:
            logger.warning(f"Skipping invalid relationship: {rel}")
            continue
            
        analysis["relationships"].append({
            "from_table": rel_dict.get("from", ""),
            "to_table": rel_dict.get("to", ""),
            "type": rel_dict.get("type", ""),
            "from_column": rel_dict.get("from_column", ""),
            "to_column": rel_dict.get("to_column", "")
        })
    
    return analysis

def build_data_prep_prompt(platform: str, model_metadata: dict, custom_requirements: str = "", kpi_list=None, data_dictionary=None, complexity: str = "intermediate") -> str:
    """Build a comprehensive prompt for data preparation that includes specific column analysis"""
    
    try:
        if not model_metadata:
            return "No data model provided. Please define your data model first."
        
        # Ensure model_metadata is a dictionary
        model_dict = safe_get_dict(model_metadata)
        if not model_dict:
            logger.error("Invalid data model format. Expected dictionary.")
            return "Invalid data model format. Please check your data model structure."
        
        analysis = analyze_data_model_for_prep(model_dict)
        tables = analysis["tables"]
        relationships = analysis["relationships"]
        
        if not tables:
            return "No valid tables found in data model. Please check your data model structure."
        
        prompt = f"""You are an expert {platform} data preparation specialist. Generate detailed, step-by-step data preparation instructions based on the following data model analysis:

## Data Model Overview:
- Total Tables: {len(tables)}
- Total Relationships: {len(relationships)}

## Detailed Table Analysis:
"""
        
        for table in tables:
            if not isinstance(table, dict):
                continue
                
            table_name = table.get("name", "Unknown")
            prompt += f"\n### Table: {table_name}\n"
            
            if table.get("primary_keys"):
                prompt += f"- Primary Keys: {', '.join(table['primary_keys'])}\n"
            if table.get("foreign_keys"):
                prompt += f"- Foreign Keys: {', '.join(table['foreign_keys'])}\n"
            if table.get("date_columns"):
                prompt += f"- Date/Time Columns: {', '.join(table['date_columns'])}\n"
            if table.get("numeric_columns"):
                prompt += f"- Numeric Columns: {', '.join(table['numeric_columns'])}\n"
            if table.get("text_columns"):
                prompt += f"- Text Columns: {', '.join(table['text_columns'])}\n"
            if table.get("nullable_columns"):
                prompt += f"- Nullable Columns: {', '.join(table['nullable_columns'])}\n"
            if table.get("potential_issues"):
                prompt += f"- ⚠️ Issues Found: {'; '.join(table['potential_issues'])}\n"
        
        # Add relationships
        if relationships:
            prompt += f"\n## Relationships:\n"
            for rel in relationships:
                if not isinstance(rel, dict):
                    continue
                from_table = rel.get("from_table", "")
                to_table = rel.get("to_table", "")
                rel_type = rel.get("type", "")
                from_col = rel.get("from_column", "")
                to_col = rel.get("to_column", "")
                prompt += f"- {from_table}.{from_col} → {to_table}.{to_col} ({rel_type})\n"
        
        # Add KPI context
        if kpi_list and len(kpi_list) > 0:
            prompt += f"\n## Key Performance Indicators (KPIs):\n"
            prompt += "Consider these KPIs when preparing data - ensure necessary calculations and groupings are available:\n"
            for i, kpi in enumerate(kpi_list[:10], 1):  # Limit to 10 KPIs
                prompt += f"{i}. **{kpi.get('name', 'Unknown KPI')}**: {kpi.get('description', 'No description')}\n"
                if kpi.get('formula'):
                    prompt += f"   Formula: {kpi['formula']}\n"
                if kpi.get('target'):
                    prompt += f"   Target: {kpi['target']}\n"
            if len(kpi_list) > 10:
                prompt += f"... and {len(kpi_list) - 10} more KPIs\n"
        
        # Add data dictionary context
        if data_dictionary:
            prompt += f"\n## Data Dictionary (Business Context):\n"
            prompt += "Use this business context to enhance data preparation steps:\n"
            for table_name, columns in list(data_dictionary.items())[:3]:  # Limit to 3 tables
                prompt += f"\n**{table_name}:**\n"
                for col_name, col_info in list(columns.items())[:5]:  # Limit to 5 columns per table
                    prompt += f"- {col_name}: {col_info.get('description', 'No description')}\n"
                    if col_info.get('type'):
                        prompt += f"  Type: {col_info['type']}\n"
                    if col_info.get('rules'):
                        prompt += f"  Business Rules: {col_info['rules']}\n"
                if len(columns) > 5:
                    prompt += f"  ... and {len(columns) - 5} more columns\n"
            if len(data_dictionary) > 3:
                prompt += f"... and {len(data_dictionary) - 3} more tables\n"
        
        # Add custom requirements
        if custom_requirements and custom_requirements.strip():
            prompt += f"\n## Additional Requirements:\n{custom_requirements}\n"
        
        # Add complexity-based instructions
        complexity_instructions = ""
        if complexity == "beginner":
            complexity_instructions = """
## IMPORTANT - BEGINNER MODE INSTRUCTIONS:

You are creating instructions for someone NEW to BI dashboards. Follow these requirements:

1. **COLUMN-BY-COLUMN DETAIL**: 
   - Create a separate subsection for EACH column that needs transformation
   - Format: "### Transforming [Column Name]: [Current Type] → [Target Type]"
   - Explain WHY this specific column needs this transformation
   - Show BEFORE and AFTER data examples for clarity

2. **STEP-BY-STEP GUIDANCE**:
   - Number every single step (1, 2, 3...)
   - Include exact button names and menu locations
   - Add screenshots references: "[Screenshot: Power Query Editor - Transform Tab]"
   - Explain what each step accomplishes

3. **EXPLANATIONS & WARNINGS**:
   - Explain technical terms in parentheses: "Change type to Decimal (a number with decimal places)"
   - Add warning boxes for common mistakes: "⚠️ WARNING: Don't select Integer for prices - you'll lose cents!"
   - Include "Why this matters" sections for each transformation

4. **VALIDATION & CHECKING**:
   - After each transformation, include: "✅ Check your work: The column should now show..."
   - Provide sample queries to verify the transformation worked
   - Include rollback instructions if something goes wrong

5. **FRIENDLY TONE**:
   - Use encouraging language: "Great job! Now let's move to the next column..."
   - Break complex concepts into simple analogies
   - Celebrate progress: "You've completed 3 of 10 transformations!"

Example format:
### Transforming OrderDate: Text → Date
**Why**: Excel stored dates as text (like "2024-01-15"), but we need real dates for time-based analysis.
**Before**: "2024-01-15" (text) | **After**: 01/15/2024 (date)
1. Click on the OrderDate column header
2. Go to Transform tab [Screenshot: Transform Tab Location]
3. Click "Data Type" button → Select "Date"
⚠️ WARNING: If you see errors, your date format might be different!
✅ Check: Column icon should now show a calendar symbol
"""
        elif complexity == "expert":
            complexity_instructions = """
## IMPORTANT - EXPERT MODE INSTRUCTIONS:

You are creating instructions for BI PROFESSIONALS. Be concise and efficient:

1. **PATTERN-BASED TRANSFORMATIONS**:
   - Group all similar columns: "Date parsing required for: OrderDate, ShipDate, DueDate, LastModified"
   - Provide the transformation pattern once, list all applicable columns
   - Focus on code/formulas over UI navigation

2. **BATCH OPERATIONS**:
   ```m
   // Apply to all date columns at once
   dateColumns = {"OrderDate", "ShipDate", "DueDate"},
   transformedDates = List.Transform(dateColumns, each {_, type date})
   ```

3. **TECHNICAL FOCUS**:
   - Assume platform expertise - skip basic navigation
   - Use technical terminology without explanation
   - Focus on performance: "Enable query folding by..."
   - Include advanced techniques: dynamic column lists, parameterized queries

4. **EDGE CASES & OPTIMIZATION**:
   - Address only non-obvious issues
   - Provide performance benchmarks where relevant
   - Include query folding considerations
   - Suggest bulk transformation strategies

5. **CODE-FIRST APPROACH**:
   - Lead with M code or SQL
   - UI steps only for non-scriptable operations
   - Include reusable functions and patterns

Example format:
**Date Columns**: Apply DateTime.FromText with culture "en-US" to: OrderDate, ShipDate, DueDate, LastModified
**Numeric Columns**: Cast to Currency.Type: Price, Cost, Tax, Discount
**Optimization**: Create column type mapping table for dynamic application across all tables
"""
        else:  # intermediate
            complexity_instructions = """
## IMPORTANT - INTERMEDIATE MODE INSTRUCTIONS:

You are creating instructions for users with SOME BI EXPERIENCE. Balance detail with efficiency:

1. **SMART GROUPING**:
   - Group similar simple transformations: "Convert all date columns (OrderDate, ShipDate, DueDate) to Date type"
   - Provide detailed steps for complex or unusual transformations
   - Show individual steps for columns with special considerations

2. **DUAL APPROACH**:
   - Provide both UI steps and code for each transformation type
   - Let users choose their preferred method
   - Example: "Via UI: Transform → Data Type → Date OR via M code: = Table.TransformColumnTypes(...)"

3. **KEY VALIDATIONS**:
   - Include validation steps for critical transformations
   - Skip validation for straightforward type changes
   - Focus on data quality checks that matter

4. **PRACTICAL FOCUS**:
   - Explain non-obvious transformations
   - Skip explanations for standard operations
   - Include tips for common scenarios
   - Assume basic platform navigation knowledge

5. **CLEAR STRUCTURE**:
   - Use headers to separate transformation types
   - Provide a summary table of all transformations at the end
   - Include "Quick Reference" sections for common patterns

Example format:
### Date Transformations
Convert these text columns to Date type: OrderDate, ShipDate, DueDate
- **UI Method**: Select columns → Transform → Data Type → Date
- **M Code**: `= Table.TransformColumnTypes(Source, {{"OrderDate", type date}, {"ShipDate", type date}})`
- **Note**: If you see errors, check the date format in your source data
"""
        
        prompt += complexity_instructions
        
        # Platform-specific instructions
        if platform.lower() == "power bi":
            prompt += f"""
## Generate Power BI Power Query M Instructions:

CRITICAL REQUIREMENT: For EVERY data transformation, provide BOTH methods:
1. **M Code Solution** - Complete M code that can be used in Advanced Editor
2. **UI/Toolbar Solution** - Step-by-step clicks using Power Query Editor interface

Format each transformation as follows:

### [Transformation Name]

**Method 1: M Code**
```m
[Provide complete M code here]
```

**Method 2: Power Query Editor UI**
1. [Step-by-step toolbar instructions]
2. [Include exact button/menu locations]
3. [Specify dialog box options]

Now provide SPECIFIC instructions for:

1. **Data Source Connection:**
   - Connection steps via UI (Get Data → Select source → Configure)
   - M code for connection string
   - Authentication requirements for both methods

2. **Column-Specific Transformations:**
   For EACH column issue identified above, provide BOTH M code AND UI steps:
   
   - **Date Columns**: 
     * M code: Change type, parse dates, handle errors
     * UI: Right-click → Change Type → Date/Time options
   
   - **Numeric Columns**: 
     * M code: Type conversion, replace values, handle nulls
     * UI: Transform tab → Data Type → Decimal/Currency
   
   - **Text Columns**: 
     * M code: Text.Trim, Text.Proper, Text.Clean
     * UI: Transform tab → Format → Trim/Clean/Capitalize

3. **Data Quality Fixes:**
   For EACH issue, show BOTH approaches:
   
   - **Remove Nulls**:
     * M code: Table.SelectRows with null check
     * UI: Filter dropdown → Uncheck null/blank
   
   - **Remove Duplicates**:
     * M code: Table.Distinct with key columns
     * UI: Home tab → Remove Rows → Remove Duplicates
   
   - **Replace Values**:
     * M code: Table.ReplaceValue function
     * UI: Right-click → Replace Values

4. **Joins and Merges:**
   - M code: Table.NestedJoin or Table.Join
   - UI: Home tab → Combine → Merge Queries

5. **Performance Optimization:**
   - Query folding best practices
   - When to use Table.Buffer
   - Native query vs UI transformations

6. **Applied Steps Documentation:**
   - How to rename steps for clarity
   - Adding comments in M code
   - Organizing transformation logic

Provide complete, copy-paste ready M code AND detailed UI navigation for EVERY transformation.
Include screenshots references where UI steps might be ambiguous.
"""
        
        elif platform.lower() == "tableau":
            prompt += f"""
## Generate Tableau Prep/Desktop Instructions:

CRITICAL REQUIREMENT: For EVERY data transformation, provide BOTH methods:
1. **Calculated Field/Custom SQL** - Complete formulas/code
2. **UI/Interface Solution** - Step-by-step clicks using Tableau Prep Builder or Desktop

Format each transformation as follows:

### [Transformation Name]

**Method 1: Calculated Field/Custom SQL**
```
[Provide complete formula or SQL here]
```

**Method 2: Tableau Interface**
1. [Step-by-step interface instructions]
2. [Include exact menu locations]
3. [Specify dialog options]

Now provide SPECIFIC instructions for:

1. **Data Connection:**
   - UI: Connect pane → Select data source → Configure options
   - Custom SQL option when needed
   - Authentication setup for both methods

2. **Column-Specific Transformations:**
   For EACH column issue, provide BOTH calculated fields AND UI steps:
   
   - **Date Columns**: 
     * Calculated field: DATEPARSE, DATE functions
     * UI: Right-click → Change Data Type → Date options
   
   - **Numeric Columns**: 
     * Calculated field: FLOAT, INT, ROUND functions
     * UI: Right-click → Change Data Type → Number options
   
   - **Text Columns**: 
     * Calculated field: TRIM, UPPER, LOWER, SPLIT
     * UI: Data pane → Create Calculated Field

3. **Data Cleaning in Tableau Prep:**
   For EACH issue, show BOTH approaches:
   
   - **Remove Nulls**:
     * Filter calculation: ISNULL() checks
     * UI: Click column → Filter → Exclude nulls
   
   - **Clean Steps**:
     * Custom clean operations
     * UI: Add Clean Step → Select cleaning options
   
   - **Pivot/Unpivot**:
     * Pivot calculations
     * UI: Add Pivot Step → Configure

4. **Joins and Relationships:**
   - Join calculations and SQL
   - UI: Data Source tab → Drag tables → Configure joins

5. **Performance Optimization:**
   - When to use extracts vs live
   - Context filters setup
   - Data engine optimization

Provide complete, copy-paste ready formulas AND detailed UI navigation for EVERY transformation.
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
        
    except Exception as e:
        logger.error(f"Error in build_data_prep_prompt: {str(e)}")
        return f"Error processing data model: {str(e)}. Please check your data model format."

def enhance_with_validation_steps(instructions: str, model_metadata: dict, platform: str) -> str:
    """Add validation and testing steps to the generated instructions"""
    
    validation_section = f"""

## 🔍 Data Validation & Quality Assurance

### Pre-Load Baseline Metrics:
1. **Document Source System Counts:**
   - Record row counts from each source table
   - Note any known data quality issues
   - Establish expected ranges based on business knowledge

### Post-Transformation Validation:"""
    
    # Add specific column validation based on model
    model_dict = safe_get_dict(model_metadata)
    analysis = analyze_data_model_for_prep(model_dict)
    tables = analysis["tables"]
    
    for table in tables:
        table_name = table["name"]
        validation_section += f"""

**{table_name} Table Validation:**"""
        
        # Primary key validation
        if table["primary_keys"]:
            for pk in table["primary_keys"]:
                validation_section += f"""
   - `{pk}`: Verify uniqueness (0 duplicates expected)
   - `{pk}`: Confirm no null values"""
        
        # Date column validation
        for col in table["date_columns"]:
            validation_section += f"""
   - `{col}`: Check date range validity (no future dates unless business rule allows)
   - `{col}`: Verify date format consistency"""
        
        # Numeric column validation
        for col in table["numeric_columns"]:
            if any(word in col.lower() for word in ["amount", "price", "cost", "salary"]):
                validation_section += f"""
   - `{col}`: Verify all values are positive (or handle negatives per business rules)
   - `{col}`: Check for outliers that may indicate data quality issues"""
        
        # Issue-specific validation
        if table["potential_issues"]:
            validation_section += f"""
   - **Data Quality Issues Fixed**: Verify the following issues are resolved:
     {', '.join(table['potential_issues'])}"""
    
    validation_section += f"""

### Relationship Integrity Checks:
3. **Foreign Key Validation:**
   - Verify all foreign key relationships have matching records
   - Check for and document any orphaned records
   - Validate referential integrity constraints

### Business Logic Validation:
4. **Domain-Specific Checks:**
   - Apply business-specific validation rules
   - Cross-check calculated fields against known totals
   - Verify aggregations match source system reports

### Performance Validation:
5. **Query Performance Testing:**
   - Test key report queries for acceptable response times
   - Monitor data refresh duration
   - Validate memory usage during processing

6. **Data Refresh Testing:**
   - Test incremental load scenarios (if applicable)
   - Verify historical data preservation
   - Check handling of late-arriving data

### Final Sign-Off Checklist:
- [ ] All source tables loaded successfully
- [ ] No critical data quality issues remain
- [ ] All relationships function correctly
- [ ] Sample reports produce expected results
- [ ] Performance meets business requirements
- [ ] Data refresh completes within acceptable timeframe
"""
    
    return instructions + validation_section

# ─── Markdown Tidier ──────────────────────────────────────────────────────────────
def tidy_md(md: str) -> str:
    """Clean up markdown formatting for better display"""
    # Blank line after any ## heading
    md = re.sub(r'(?m)^(## .+)$', r'\1\n', md)
    # Start numbered lists on a new line
    md = re.sub(r'(?m)^(\d+\.)', r'\n\1', md)
    # Indent any dash bullets
    md = re.sub(r'(?m)^\s*-\s+', r'  - ', md)
    return md.strip()

# ─── AI Vision Image Analysis (NEW) ──────────────────────────────────────────────
@app.post("/api/v1/analyze-image")
async def analyze_dashboard_image(
    file: UploadFile = File(...), 
    platform: str = Form(default="Power BI")
):
    """Analyze dashboard wireframe/sketch using GPT-4 Vision"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image (PNG, JPG, JPEG, GIF)")
        
        # Check file size (limit to 10MB)
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(400, "File size too large. Please use an image smaller than 10MB.")
        
        if file_size == 0:
            raise HTTPException(400, "File is empty.")
        
        # Encode image
        base64_image = base64.b64encode(file_content).decode('utf-8')
        
        logger.info(f"Analyzing image: {file.filename}, size: {file_size} bytes, platform: {platform}")
        
        # Choose model based on image complexity - GPT-4o for all images for best accuracy
        # For very simple wireframes, could use gpt-4o-mini, but gpt-4o gives better results
        model_to_use = "gpt-4o"  # Stick with best model for accuracy
        
        # Create AI vision prompt
        system_msg = f"""You are an expert {platform} dashboard design analyst. Analyze the uploaded wireframe, sketch, or screenshot and provide a structured layout description.

Focus on identifying:
1. **Layout Structure**: Overall organization (grid, sections, positioning)
2. **Visual Components**: KPIs, charts, tables, slicers, filters, buttons
3. **Positioning**: Top, bottom, left, right, center areas
4. **Visual Types**: Bar charts, line charts, pie charts, tables, cards, etc. 
5. **Text/Labels**: Any visible titles, labels, or annotations
6. **Relationships**: How components relate to each other

Provide a clear, structured description that can be used to generate specific {platform} implementation instructions."""

        user_msg = f"""Analyze this dashboard wireframe/sketch for {platform}. 

Please provide:
1. A summary of the overall layout
2. Detailed description of each visual component and its position
3. Any text or labels you can identify
4. Suggested {platform} visual types for implementation

Be specific about positioning (top-left, center, bottom-right, etc.) and visual types."""

        # Prepare messages for vision API call
        vision_messages = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_msg},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"  # Keep high detail for accurate analysis
                        }
                    }
                ]
            }
        ]
        
        # Call GPT-4o Vision with much longer timeout - revert to working settings
        layout_description = create_vision_call_with_retry(
            messages=vision_messages,
            max_tokens=2000,  # Increased for more detailed analysis
            timeout=900,      # 15 minutes timeout - matches other vision calls
            max_retries=2     # 3 total attempts
        )
        
        logger.info(f"AI Vision analysis completed for {file.filename}")
        
        return {
            "layout_description": layout_description,
            "platform": platform,
            "processing_method": "ai_vision",
            "file_name": file.filename,
            "file_size": file_size,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image {file.filename if file else 'unknown'}: {str(e)}")
        raise HTTPException(500, f"Image analysis failed: {str(e)}")

# ─── Simple Shape Detection (Fallback) ───────────────────────────────────────────
@app.post("/api/v1/detect-layout")
async def detect_simple_layout(file: UploadFile = File(...)):
    """Fallback: Simple geometric layout detection using OpenCV"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        # Read image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(400, "File is empty")
        
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        img_array = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect shapes using edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Apply morphological operations to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        layout_elements = []
        img_height, img_width = gray.shape
        min_area = (img_width * img_height * 0.005)  # At least 0.5% of image
        
        logger.info(f"Image size: {img_width}x{img_height}, found {len(contours)} contours")
        
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter significant shapes
            if area > min_area and w > 20 and h > 20:  # Minimum size thresholds
                # Determine position
                y_center = y + h/2
                x_center = x + w/2
                
                # Vertical position
                if y_center < img_height * 0.25:
                    v_pos = "top"
                elif y_center > img_height * 0.75:
                    v_pos = "bottom"
                else:
                    v_pos = "middle"
                
                # Horizontal position
                if x_center < img_width * 0.25:
                    h_pos = "left"
                elif x_center > img_width * 0.75:
                    h_pos = "right"
                else:
                    h_pos = "center"
                
                position = f"{v_pos}-{h_pos}"
                
                # Determine likely visual type based on dimensions
                aspect_ratio = w / h
                if aspect_ratio > 3:
                    visual_type = "wide chart or table header"
                elif aspect_ratio > 1.5:
                    visual_type = "horizontal chart or table"
                elif aspect_ratio < 0.3:
                    visual_type = "vertical chart or slicer"
                elif 0.7 <= aspect_ratio <= 1.3:
                    visual_type = "KPI card or square chart"
                else:
                    visual_type = "chart or visual element"
                
                layout_elements.append({
                    "position": position,
                    "type": visual_type,
                    "dimensions": f"{w}×{h}px",
                    "area_percent": round((area / (img_width * img_height)) * 100, 1)
                })
        
        # Sort by position (top to bottom, left to right)
        layout_elements.sort(key=lambda x: (
            0 if "top" in x["position"] else 1 if "middle" in x["position"] else 2,
            0 if "left" in x["position"] else 1 if "center" in x["position"] else 2
        ))
        
        if not layout_elements:
            layout_description = """No clear layout structure detected from geometric analysis.

This could be because:
- The image has low contrast or unclear boundaries
- The layout is hand-drawn without distinct shapes
- The image quality needs improvement

Suggestions:
- Try the AI Vision analysis for better results
- Use a clearer image with distinct visual boundaries
- Or describe the layout manually"""
        else:
            layout_description = f"Detected {len(layout_elements)} layout elements:\n\n"
            for i, element in enumerate(layout_elements, 1):
                layout_description += f"{i}. **{element['position'].title()}**: {element['type']} ({element['dimensions']}, {element['area_percent']}% of image)\n"
            
            layout_description += f"\n**Analysis Summary:**\n"
            layout_description += f"- Total elements detected: {len(layout_elements)}\n"
            layout_description += f"- Image dimensions: {img_width}×{img_height}px\n"
            layout_description += f"- Processing method: Geometric shape detection\n"
        
        logger.info(f"Shape detection completed: found {len(layout_elements)} elements")
        
        return {
            "layout_description": layout_description,
            "processing_method": "shape_detection",
            "elements_found": len(layout_elements),
            "elements": layout_elements,
            "image_dimensions": {"width": img_width, "height": img_height},
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in shape detection: {str(e)}")
        raise HTTPException(500, f"Layout detection failed: {str(e)}")

# ─── Unstructured Notes Parsing ─────────────────────────────────────────────────
class UnstructuredKPIRequest(BaseModel):
    notes_text: str

class UnstructuredKPIResponse(BaseModel):
    kpi_list: List[Dict[str, str]]
    parsing_notes: str

class UnstructuredDictRequest(BaseModel):
    notes_text: str
    table_context: Optional[str] = ""

class UnstructuredDictResponse(BaseModel):
    data_dictionary: Dict[str, Dict[str, Dict[str, str]]]
    parsing_notes: str

@app.post("/api/v1/parse-unstructured-kpis", response_model=UnstructuredKPIResponse)
async def parse_unstructured_kpis(req: UnstructuredKPIRequest):
    """Parse unstructured notes into structured KPI definitions"""
    try:
        if not req.notes_text or len(req.notes_text.strip()) < 10:
            raise HTTPException(400, "Notes text is too short. Please provide more detailed KPI information.")
        
        system_msg = """You are an expert business analyst. Parse unstructured notes about KPIs and metrics into a structured JSON format.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no explanations
- Extract all mentioned KPIs, metrics, and performance indicators
- Infer reasonable descriptions if not explicitly stated
- Include formulas when mathematical expressions are mentioned
- Add targets when numbers or thresholds are mentioned
- Categorize KPIs when context suggests groupings

Expected JSON format:
{
  "kpi_list": [
    {
      "name": "KPI Name",
      "description": "Clear business description", 
      "formula": "Mathematical calculation if mentioned",
      "target": "Target value if mentioned",
      "category": "Category if inferable",
      "frequency": "Reporting frequency if mentioned",
      "owner": "Business owner if mentioned"
    }
  ],
  "parsing_notes": "Brief summary of what was extracted and any assumptions made"
}

Examples of what to extract:
- "Sales revenue should be at least $2M monthly" → KPI with target
- "Customer satisfaction score" → KPI needing description
- "Profit margin = (Revenue - Costs) / Revenue" → KPI with formula
- "Marketing metrics: CTR, conversion rate, CAC" → Multiple KPIs in category
"""

        user_msg = f"""Parse these unstructured notes into structured KPI definitions:

{req.notes_text}

Extract all performance indicators, metrics, and KPIs mentioned. Include formulas, targets, and business context where available."""

        content = create_optimized_openai_call(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=2000,
            timeout=600
        )
        
        # Clean and parse response
        content = content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '')
        if content.startswith('```'):
            content = content.replace('```', '')
        
        parsed = json.loads(content)
        
        # Validate result
        if not parsed.get("kpi_list") or not isinstance(parsed["kpi_list"], list):
            raise ValueError("No valid KPIs extracted from notes")
        
        # Ensure all KPIs have required fields
        for kpi in parsed["kpi_list"]:
            if not kpi.get("name"):
                kpi["name"] = "Unnamed Metric"
            if not kpi.get("description"):
                kpi["description"] = "Description needs to be defined"
        
        
        return UnstructuredKPIResponse(
            kpi_list=parsed["kpi_list"],
            parsing_notes=parsed.get("parsing_notes", "Successfully extracted KPIs from provided notes")
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        raise HTTPException(500, "AI generated invalid response. Please try rephrasing your notes or contact support.")
    
    except Exception as e:
        logger.error(f"Unstructured KPI parsing failed: {str(e)}")
        raise HTTPException(500, f"KPI parsing failed: {str(e)}")

@app.post("/api/v1/parse-unstructured-dictionary", response_model=UnstructuredDictResponse)
async def parse_unstructured_dictionary(req: UnstructuredDictRequest):
    """Parse unstructured notes into structured data dictionary"""
    try:
        if not req.notes_text or len(req.notes_text.strip()) < 10:
            raise HTTPException(400, "Notes text is too short. Please provide more detailed data dictionary information.")
        
        system_msg = """You are an expert data architect. Parse unstructured notes about data fields and tables into a structured data dictionary JSON format.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no explanations
- Extract all mentioned tables, fields, and data elements
- Infer reasonable descriptions for fields when not explicit
- Include data types when mentioned or inferable
- Add business rules when constraints or validations are mentioned
- Group fields by table when structure is apparent

Expected JSON format:
{
  "data_dictionary": {
    "table_name": {
      "field_name": {
        "description": "Business meaning of the field",
        "type": "Data type if mentioned (string, int, date, etc.)",
        "rules": "Business rules or constraints if mentioned",
        "example": "Example values if provided"
      }
    }
  },
  "parsing_notes": "Brief summary of what was extracted and any assumptions made"
}

Examples of what to extract:
- "Customer table has customer_id, name, email" → Table with 3 fields
- "Sales amount must be positive number" → Field with business rule
- "Order date format: YYYY-MM-DD" → Field with type and format rule
- "Product categories: Electronics, Clothing, Books" → Field with example values
"""

        context_prompt = ""
        if req.table_context:
            context_prompt = f"\n\nAdditional context about tables/structure:\n{req.table_context}"

        user_msg = f"""Parse these unstructured notes into a structured data dictionary:

{req.notes_text}{context_prompt}

Extract all data fields, tables, and business rules mentioned. Include data types, constraints, and business context where available."""

        content = create_optimized_openai_call(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=2000,
            timeout=600
        )
        
        # Clean and parse response
        content = content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '')
        if content.startswith('```'):
            content = content.replace('```', '')
        
        parsed = json.loads(content)
        
        # Validate result
        if not parsed.get("data_dictionary") or not isinstance(parsed["data_dictionary"], dict):
            raise ValueError("No valid data dictionary extracted from notes")
        
        # Ensure all fields have required structure
        for table_name, fields in parsed["data_dictionary"].items():
            if not isinstance(fields, dict):
                continue
            for field_name, field_info in fields.items():
                if not isinstance(field_info, dict):
                    parsed["data_dictionary"][table_name][field_name] = {"description": str(field_info)}
                elif not field_info.get("description"):
                    field_info["description"] = "Description needs to be defined"
        
        total_fields = sum(len(fields) for fields in parsed["data_dictionary"].values())
        
        return UnstructuredDictResponse(
            data_dictionary=parsed["data_dictionary"],
            parsing_notes=parsed.get("parsing_notes", f"Successfully extracted {len(parsed['data_dictionary'])} tables with {total_fields} fields from provided notes")
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        raise HTTPException(500, "AI generated invalid response. Please try rephrasing your notes or contact support.")
    
    except Exception as e:
        logger.error(f"Unstructured dictionary parsing failed: {str(e)}")
        raise HTTPException(500, f"Data dictionary parsing failed: {str(e)}")

# ─── Enhanced Screenshot Parsing ─────────────────────────────────────────────────
@app.post("/api/v1/parse-screenshot-enhanced")
async def parse_screenshot_enhanced(
    file: UploadFile = File(...), 
    method: str = Form(default="ai_vision")
):
    """Enhanced screenshot parsing with multiple methods"""
    try:
        logger.info(f"Enhanced screenshot parsing with method: {method}")
        
        if method == "ai_vision":
            # Use AI vision analysis
            result = await analyze_dashboard_image(file, "Generic")
            description = result["layout_description"]
            
            # Convert AI description to simple sections for compatibility
            sections = []
            lines = [line.strip() for line in description.split('\n') if line.strip()]
            
            section_count = 0
            for line in lines[:8]:  # Limit to 8 sections
                if any(word in line.lower() for word in ['kpi', 'chart', 'table', 'slicer', 'visual', 'card', 'graph']):
                    if 'kpi' in line.lower() or 'card' in line.lower():
                        section_type = "KPI"
                    elif 'table' in line.lower():
                        section_type = "Table"
                    else:
                        section_type = "Chart"
                    
                    if 'top' in line.lower():
                        section_position = "top"
                    elif 'bottom' in line.lower():
                        section_position = "bottom"
                    else:
                        section_position = "main"
                    
                    sections.append({
                        "layout_type": section_type,
                        "section": section_position,
                        "label": line[:100]  # Truncate for display
                    })
                    section_count += 1
            
            if not sections:
                # Fallback if no specific elements detected
                sections = [{
                    "layout_type": "Chart",
                    "section": "main", 
                    "label": "AI analyzed dashboard layout"
                }]
            
            logger.info(f"AI Vision parsing returned {len(sections)} sections")
            return sections
            
        else:
            # Use simple detection as fallback
            result = await detect_simple_layout(file)
            description = result["layout_description"]
            
            # Convert simple detection to sections
            sections = [{
                "layout_type": "Chart",
                "section": "main", 
                "label": f"Simple detection found {result.get('elements_found', 0)} elements"
            }]
            
            return sections
            
    except Exception as e:
        logger.error(f"Enhanced screenshot parsing failed: {str(e)}")
        # Return minimal fallback response
        return [{
            "layout_type": "Chart", 
            "section": "main", 
            "label": f"Processing failed - try manual description"
        }]

# ─── Model Generation from SQL ───────────────────────────────────────────────────
@app.post("/api/v1/generate-model", response_model=ModelGenResponse)
async def generate_model(req: ModelGenRequest):
    """Cost-optimized model generation - Smart processing with minimal API calls"""
    try:
        # Calculate total input size
        total_size = sum(len(ddl) for ddl in req.tables_sql) + len(req.relationships_sql)
        logger.info(f"Processing {len(req.tables_sql)} DDL files, total size: {total_size} chars")
        
        # SMART SIZING: Determine processing approach based on size
        if total_size > 30000:  # Very large schema
            raise HTTPException(400, 
                f"Schema too large ({total_size:,} characters). "
                "Please use the Enterprise Template approach or focus on core tables (10-20 most important tables)."
            )
        
        elif total_size > 15000:  # Large schema - Use chunking but fewer chunks
            logger.info("Large schema detected - using optimized 2-chunk processing")
            return await process_large_schema_optimized(req, total_size)
        
        else:  # Medium/Small schema - Single API call
            logger.info("Medium/small schema - using single API call")
            return await process_schema_single_call(req, total_size)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model generation error: {str(e)}")
        raise HTTPException(500, f"Model generation failed: {str(e)}")


async def process_schema_single_call(req: ModelGenRequest, total_size: int):
    """Process schema with single API call - most cost effective"""
    
    # Combine all DDLs into one optimized prompt
    combined_ddl = "\n\n--- TABLE DEFINITIONS ---\n" + "\n\n".join(req.tables_sql)
    
    if req.relationships_sql.strip():
        combined_ddl += "\n\n--- RELATIONSHIPS ---\n" + req.relationships_sql
    
    # Optimized system prompt for better results with single call
    system_msg = """You are a data modeling expert. Convert SQL DDL to a clean JSON data model.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no explanations
- Use simple types: 'string', 'int', 'date', 'decimal', 'boolean'  
- Extract ALL table definitions provided
- Include relationships from foreign key constraints
- Handle Salesforce-style field names (with __c)

Expected JSON format:
{
  "tables": [
    {
      "name": "TABLE_NAME",
      "columns": [
        {"name": "COLUMN_NAME", "type": "string", "nullable": true, "is_primary_key": false, "is_foreign_key": false}
      ]
    }
  ],
  "relationships": [
    {"from": "table1", "to": "table2", "from_column": "col1", "to_column": "col2", "type": "many-to-one"}
  ]
}"""

    try:
        # Single API call with optimized settings
        content = create_optimized_openai_call(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": combined_ddl}
            ],
            max_tokens=min(4000, max(1500, total_size // 3)),  # Dynamic token allocation
            timeout=120  # Reasonable timeout
        )
        
        # Clean and parse response
        content = content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '')
        if content.startswith('```'):
            content = content.replace('```', '')
        
        # Handle common JSON issues
        content = content.replace('\n', ' ').replace('\t', ' ')
        while '  ' in content:
            content = content.replace('  ', ' ')
        
        parsed = json.loads(content)
        
        # Validate result
        if not parsed.get("tables") or len(parsed["tables"]) == 0:
            raise ValueError("No tables generated")
        
        return ModelGenResponse(data_model=parsed)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        # Fallback: Try to extract valid JSON from response
        try:
            # Look for JSON-like content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                clean_json = content[json_start:json_end]
                parsed = json.loads(clean_json)
                return ModelGenResponse(data_model=parsed)
        except:
            pass
        
        raise HTTPException(500, f"AI generated invalid JSON. Try with fewer tables or use Enterprise Template approach.")
    
    except Exception as e:
        logger.error(f"Single call processing failed: {str(e)}")
        raise HTTPException(500, f"Processing failed: {str(e)}")


async def process_large_schema_optimized(req: ModelGenRequest, total_size: int):
    """Process large schema with minimal chunking - 2 API calls maximum"""
    
    logger.info("Using cost-optimized large schema processing")
    
    # Smart chunking: Split into 2 roughly equal chunks
    mid_point = len(req.tables_sql) // 2
    chunk1_ddls = req.tables_sql[:mid_point]
    chunk2_ddls = req.tables_sql[mid_point:]
    
    all_tables = []
    all_relationships = []
    
    # Process first chunk
    try:
        chunk1_result = await process_ddl_chunk(chunk1_ddls, 1, 2)
        if chunk1_result and "tables" in chunk1_result:
            all_tables.extend(chunk1_result["tables"])
            logger.info(f"Chunk 1: Added {len(chunk1_result['tables'])} tables")
    except Exception as e:
        logger.warning(f"Chunk 1 failed: {str(e)}")
    
    # Process second chunk
    try:
        chunk2_result = await process_ddl_chunk(chunk2_ddls, 2, 2)
        if chunk2_result and "tables" in chunk2_result:
            all_tables.extend(chunk2_result["tables"])
            logger.info(f"Chunk 2: Added {len(chunk2_result['tables'])} tables")
    except Exception as e:
        logger.warning(f"Chunk 2 failed: {str(e)}")
    
    # Process relationships (if any tables were successful)
    if all_tables and req.relationships_sql.strip():
        try:
            rel_result = await process_relationships_only(req.relationships_sql)
            if rel_result:
                all_relationships = rel_result
        except Exception as e:
            logger.warning(f"Relationships processing failed: {str(e)}")
    
    if not all_tables:
        raise HTTPException(500, "Failed to process any tables. Try with fewer tables or use Enterprise Template.")
    
    final_model = {
        "tables": all_tables,
        "relationships": all_relationships
    }
    
    return ModelGenResponse(data_model=final_model)


async def process_ddl_chunk(ddl_list, chunk_num, total_chunks):
    """Process a chunk of DDL files efficiently"""
    
    combined_ddl = "\n\n".join(ddl_list)
    
    system_msg = f"""Convert SQL DDL chunk {chunk_num}/{total_chunks} to JSON.
Return ONLY valid JSON with tables array. Use types: string, int, date, decimal.
Format: {{"tables": [{{"name": "table", "columns": [{{"name": "col", "type": "string", "nullable": true, "is_primary_key": false, "is_foreign_key": false}}]}}]}}"""
    
    content = create_optimized_openai_call(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Tables:\n{combined_ddl}"}
        ],
        max_tokens=2000,
        timeout=600
    )
    
    # Clean and parse
    content = content.strip()
    if content.startswith('```json'):
        content = content.replace('```json', '').replace('```', '')
    if content.startswith('```'):
        content = content.replace('```', '')
    
    return json.loads(content)


async def process_relationships_only(relationships_sql):
    """Process relationships with minimal API call"""
    
    system_msg = "Extract relationships from SQL. Return JSON: {'relationships': [...]}"
    
    content = create_optimized_openai_call(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": relationships_sql}
        ],
        max_tokens=800,
        timeout=600
    )
    
    content = content.strip()
    if content.startswith('```json'):
        content = content.replace('```json', '').replace('```', '')
    
    result = json.loads(content)
    return result.get("relationships", [])

# ─── Layout or Data Prep Generation ─────────────────────────────────────────────
@app.post("/api/v1/generate-layout", response_model=GenerateResponse)
async def generate_layout(req: GenerateRequest):
    """Generate layout instructions or data preparation steps"""
    import time
    start_time = time.time()
    
    try:
        logger.info(f"🚀 **BACKEND**: Starting generate-layout request at {time.strftime('%H:%M:%S')}")
        logger.info(f"📊 **REQUEST INFO**: Platform: {req.platform_selected}, Data prep only: {req.data_prep_only}")
        
        # Data-Prep Only branch - ENHANCED VERSION with error handling
        if req.data_prep_only:
            # Validate input
            if not req.model_metadata:
                raise HTTPException(
                    status_code=400, 
                    detail="model_metadata is required for data preparation"
                )
            
            if not req.platform_selected:
                raise HTTPException(
                    status_code=400,
                    detail="platform_selected is required"
                )
            
            logger.info(f"Generating data prep for {req.platform_selected}")
            
            
            # Ensure model_metadata is properly formatted
            model_dict = safe_get_dict(req.model_metadata)
            if not model_dict:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid model_metadata format. Expected dictionary with 'tables' and 'relationships' keys."
                )
            
            tables = safe_get_list(model_dict.get("tables", []))
            logger.info(f"Found {len(tables)} tables in model")
            
            if not tables:
                raise HTTPException(
                    status_code=400,
                    detail="No tables found in model_metadata. Please check your data model structure."
                )
            
            # Build comprehensive prompt with error handling
            try:
                enhanced_prompt = build_data_prep_prompt(
                    platform=req.platform_selected,
                    model_metadata=model_dict,  # Use the safely parsed dictionary
                    custom_requirements=req.custom_prompt or "",
                    kpi_list=req.kpi_list,
                    data_dictionary=req.data_dictionary,
                    complexity=req.instruction_complexity or "intermediate"
                )
            except Exception as prompt_error:
                logger.error(f"Error building prompt: {str(prompt_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error analyzing data model: {str(prompt_error)}"
                )
            
            system_msg = (
                f"You are a senior {req.platform_selected} data engineer with 10+ years experience. "
                "Generate SPECIFIC, actionable data preparation instructions. "
                "Reference exact column names from the data model. "
                "Include code snippets, validation steps, and troubleshooting tips. "
                "Be precise about data types, null handling, and business rules. "
                "Address each data quality issue identified in the analysis."
            )
            
            # Updated for OpenAI v1.0+
            try:
                raw_instructions = create_optimized_openai_call(
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=2500,  # Reduced to speed up response
                    timeout=600
                )
            except Exception as openai_error:
                logger.error(f"OpenAI timeout or error: {str(openai_error)}")
                # Provide a fallback response
                raw_instructions = f"""
# {req.platform_selected} Data Preparation Steps

## Data Model Analysis
Your data model has been analyzed and the following issues were identified:
- Please check your OpenAI API key and connection
- The AI service is currently experiencing delays

## Basic Data Preparation Steps
1. **Connect to your data source**
2. **Clean data types for each column**
3. **Handle null values appropriately**
4. **Set up table relationships**
5. **Validate data quality**

Please try again or contact support if the issue persists.
"""
            
            # Post-process to add validation sections
            final_instructions = enhance_with_validation_steps(
                raw_instructions, 
                model_dict,  # Use the parsed dictionary
                req.platform_selected
            )
            
            elapsed_time = time.time() - start_time
            
            return GenerateResponse(
                wireframe_json="", 
                layout_instructions=tidy_md(final_instructions)
            )

        # Full Layout branch
        system_msg = (
            f"You are an AI expert in BI dashboards for {req.platform_selected}.  \n"
            "**First**, under `## Measures`, list each measure or calculated column with exact formula (DAX or Tableau calc).  \n"
            "**Then**, for each visual, output `## <VisualType>` and a numbered Markdown list:\n"
            "1. Which visual to insert\n"
            "2. Fields in Values/Axis/Legend/Tooltips\n"
            "3. Sorts, filters, groupings\n"
            "4. Suggested formatting\n\n"
            "IMPORTANT: If KPI definitions are provided, prioritize these metrics in your dashboard layout. "
            "If a data dictionary is provided, use the business context to make informed decisions about field usage and visualization types.\n\n"
            "Return only valid JSON with keys:\n"
            "• wireframe_json: the original sketch_description (as object)\n"
            "• layout_instructions: the Markdown instructions"
        )
        
        # Analyze model complexity to optimize payload and timeout
        model_dict = safe_get_dict(req.model_metadata or {})
        tables = safe_get_list(model_dict.get("tables", []))
        total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
        
        # Determine complexity and optimize accordingly
        is_complex = len(tables) > 10 or total_columns > 100
        is_simple = len(tables) <= 5 and total_columns <= 50
        
        logger.info(f"Dashboard generation: {len(tables)} tables, {total_columns} columns, complex: {is_complex}")
        
        # Build optimized user message based on complexity
        user_msg_data = {
            "sketch_description": req.sketch_description,
            "custom_prompt": req.custom_prompt,
        }
        
        # Optimize model metadata based on complexity
        if is_complex:
            # For complex models, send only essential info
            simplified_model = {
                "tables": []
            }
            for table in tables[:15]:  # Limit to 15 tables
                table_dict = safe_get_dict(table)
                if table_dict:
                    table_name = table_dict.get("table_name", "") or table_dict.get("name", "")
                    columns = safe_get_list(table_dict.get("columns", []))
                    
                    # Simplify columns - keep only essential info
                    simplified_columns = []
                    for col in columns[:10]:  # Limit to 10 columns per table
                        if isinstance(col, str):
                            simplified_columns.append(col)
                        else:
                            col_dict = safe_get_dict(col)
                            if col_dict:
                                col_name = col_dict.get("column_name", "") or col_dict.get("name", "")
                                col_type = col_dict.get("data_type", "") or col_dict.get("type", "")
                                simplified_columns.append(f"{col_name} ({col_type})")
                    
                    simplified_model["tables"].append({
                        "name": table_name,
                        "columns": simplified_columns
                    })
            user_msg_data["model_metadata"] = simplified_model
        else:
            # For simple models, send full metadata
            user_msg_data["model_metadata"] = req.model_metadata
        
        # Add KPI context to user message (adjust limits based on complexity)
        if req.kpi_list:
            kpi_limit = 5 if is_complex else 10
            user_msg_data["kpi_definitions"] = req.kpi_list[:kpi_limit]
        
        # Add data dictionary context (adjust limits based on complexity)
        if req.data_dictionary:
            simplified_dict = {}
            table_limit = 2 if is_complex else 3
            col_limit = 3 if is_complex else 5
            for table_name, columns in list(req.data_dictionary.items())[:table_limit]:
                simplified_dict[table_name] = {}
                for col_name, col_info in list(columns.items())[:col_limit]:
                    simplified_dict[table_name][col_name] = col_info.get('description', 'No description')
            user_msg_data["data_dictionary"] = simplified_dict
        
        user_msg = json.dumps(user_msg_data, indent=2)
        
        # Dynamic timeout and token allocation based on complexity
        if is_complex:
            timeout_seconds = 900  # 15 minutes for complex models
            max_tokens = 2500
        elif is_simple:
            timeout_seconds = 600   # 10 minutes for simple models
            max_tokens = 1500
        else:
            timeout_seconds = 720  # 12 minutes for medium models
            max_tokens = 1800
        
        logger.info(f"Using timeout: {timeout_seconds}s, max_tokens: {max_tokens}")
        
        # Updated for OpenAI v1.0+
        try:
            content = create_optimized_openai_call(
                messages=[
                    {"role":"system","content":system_msg},
                    {"role":"user","content":user_msg}
                ],
                max_tokens=max_tokens,
                timeout=timeout_seconds
            )
        except Exception as e:
            # Fallback for layout generation
            content = json.dumps({
                "wireframe_json": req.sketch_description,
                "layout_instructions": "AI service temporarily unavailable. Please try again."
            })

        # Parse JSON from the AI, then tidy the instructions
        try:
            result = json.loads(content)
            instr = tidy_md(result.get("layout_instructions",""))
            return GenerateResponse(
                wireframe_json=result.get("wireframe_json",""),
                layout_instructions=instr
            )
        except Exception as parse_error:
            logger.warning(f"Failed to parse AI response as JSON: {str(parse_error)}")
            
            # Enhanced JSON extraction with better regex patterns
            try:
                # Try multiple patterns to extract layout_instructions
                patterns = [
                    # Standard JSON field with escaped quotes
                    r'"layout_instructions":\s*"([^"]*(?:\\.[^"]*)*)"',
                    # JSON field with single quotes 
                    r"'layout_instructions':\s*'([^']*(?:\\.[^']*)*)'",
                    # Multiline JSON field
                    r'"layout_instructions":\s*"((?:[^"\\]|\\.)*)"\s*[,}]',
                    # Without quotes (if AI returns unquoted)
                    r'"layout_instructions":\s*([^,}]+)',
                    # Alternative field names
                    r'"instructions":\s*"([^"]*(?:\\.[^"]*)*)"',
                    r'"dashboard_instructions":\s*"([^"]*(?:\\.[^"]*)*)"'
                ]
                
                extracted_instructions = None
                for pattern in patterns:
                    layout_match = re.search(pattern, content, re.DOTALL)
                    if layout_match:
                        extracted_instructions = layout_match.group(1)
                        break
                
                if extracted_instructions:
                    # Comprehensive unescape
                    extracted_instructions = extracted_instructions.replace('\\"', '"')
                    extracted_instructions = extracted_instructions.replace('\\n', '\n')
                    extracted_instructions = extracted_instructions.replace('\\r', '\r')
                    extracted_instructions = extracted_instructions.replace('\\t', '\t')
                    extracted_instructions = extracted_instructions.replace('\\\\', '\\')
                    
                    # Clean up common AI artifacts
                    extracted_instructions = re.sub(r'\\[a-z]', '', extracted_instructions)  # Remove escape sequences
                    extracted_instructions = re.sub(r'[∗∧¨◊]+', '', extracted_instructions)  # Remove Unicode artifacts
                    
                    return GenerateResponse(
                        wireframe_json="",
                        layout_instructions=tidy_md(extracted_instructions)
                    )
                    
            except Exception as extract_error:
                logger.warning(f"Failed to extract layout_instructions: {str(extract_error)}")
            
            # Final fallback: return raw content with basic cleanup
            cleaned_content = content
            
            # Remove obvious JSON structure artifacts
            cleaned_content = re.sub(r'^\s*{\s*', '', cleaned_content)  # Remove opening brace
            cleaned_content = re.sub(r'\s*}\s*$', '', cleaned_content)  # Remove closing brace
            cleaned_content = re.sub(r'"wireframe_json":\s*[^,}]+,?\s*', '', cleaned_content)  # Remove wireframe_json
            cleaned_content = re.sub(r'"[^"]*":\s*"[^"]*",?\s*', '', cleaned_content)  # Remove other JSON fields
            
            # Basic cleanup
            cleaned_content = cleaned_content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            cleaned_content = re.sub(r'[∗∧¨◊]+', '', cleaned_content)  # Remove Unicode artifacts
            
            # If still looks like JSON, just return the original for frontend to handle
            if cleaned_content.strip().startswith('{') and cleaned_content.strip().endswith('}'):
                return GenerateResponse(wireframe_json="", layout_instructions=content)
            
            return GenerateResponse(wireframe_json="", layout_instructions=tidy_md(cleaned_content))

    except HTTPException:
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ **BACKEND**: Error in generate_layout after {elapsed_time:.1f} seconds: {str(e)}")
        logger.error(f"Request model_metadata type: {type(req.model_metadata)}")
        logger.error(f"Request data preview: {str(req.model_metadata)[:200]}...")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error after {elapsed_time:.1f}s: {str(e)}"
        )

# ─── Sprint Board Generation ────────────────────────────────────────────────────
@app.post("/api/v1/generate-sprint", response_model=SprintResponse)
async def generate_sprint(req: SprintRequest):
    """Generate sprint backlog from dashboard development instructions"""
    try:
        system_msg = (
            "You are an AI that converts dashboard prep & dev steps into Scrum sprint stories.  \n"
            "Input:\n"
            "- layout_instructions (Markdown)\n"
            "- sprint_length_days\n"
            "- velocity\n\n"
            "Return only JSON with:\n"
            "• sprint_stories: [ {title, points, description}, ... ]\n"
            "• over_under_capacity: integer\n"
        )
        user_msg = json.dumps({
            "layout_instructions": req.layout_instructions,
            "sprint_length_days":  req.sprint_length_days,
            "velocity":            req.velocity
        }, indent=2)
        
        # Updated for OpenAI v1.0+
        try:
            content = create_optimized_openai_call(
                messages=[
                    {"role":"system","content":system_msg},
                    {"role":"user","content":user_msg}
                ],
                max_tokens=1200,
                timeout=600
            )
        except Exception as e:
            raise HTTPException(500, f"Sprint generation failed: {str(e)}")
        
        try:
            parsed = json.loads(content)
        except Exception as e:
            raise HTTPException(500, f"Invalid JSON from AI:\n{e}\n\n{content}")
        
        return SprintResponse(
            sprint_stories=parsed.get("sprint_stories",[]),
            over_under_capacity=parsed.get("over_under_capacity",0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_sprint: {str(e)}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

# ─── Health Check ────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Agentic BI Assistant"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)