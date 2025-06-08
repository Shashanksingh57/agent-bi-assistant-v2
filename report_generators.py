# report_generators.py - Report generation helper functions

from datetime import datetime

def safe_get_dict(obj, default=None):
    """Safely get dictionary from object, handling string/None cases"""
    if obj is None:
        return default or {}
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, str):
        try:
            import json
            return json.loads(obj)
        except:
            return default or {}
    return default or {}

def safe_get_list(obj, default=None):
    """Safely get list from object, handling various input types"""
    if obj is None:
        return default or []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, str):
        try:
            import json
            parsed = json.loads(obj)
            if isinstance(parsed, list):
                return parsed
        except:
            pass
    return default or []

def analyze_model_complexity(model_metadata):
    """Analyze the complexity of the data model"""
    if not model_metadata:
        return "Unknown"
    
    model_dict = safe_get_dict(model_metadata)
    if not model_dict:
        return "Unknown"
    
    tables = safe_get_list(model_dict.get("tables", []))
    relationships = safe_get_list(model_dict.get("relationships", []))
    
    total_columns = 0
    for table in tables:
        table_dict = safe_get_dict(table)
        if table_dict:
            columns = safe_get_list(table_dict.get("columns", []))
            total_columns += len(columns)
    
    if len(tables) <= 3 and total_columns <= 20 and len(relationships) <= 3:
        return "Simple"
    elif len(tables) <= 10 and total_columns <= 100 and len(relationships) <= 10:
        return "Moderate"
    else:
        return "Complex"

def generate_kpi_summary_text(kpi_list):
    """Generate a text summary of KPIs for copy/paste"""
    if not kpi_list:
        return "No KPIs defined."
    
    summary = f"# KPI Summary ({len(kpi_list)} metrics)\n\n"
    
    for i, kpi in enumerate(kpi_list, 1):
        name = kpi.get('name', f'KPI {i}')
        description = kpi.get('description', 'No description')
        summary += f"**{i}. {name}**\n"
        summary += f"   {description}\n\n"
    
    return summary

def generate_kpi_business_report(kpi_list):
    """Generate a comprehensive business report for KPIs"""
    if not kpi_list:
        return "No KPIs available for report generation."
    
    report = f"""# Key Performance Indicators Report
Generated on: {datetime.now().strftime('%B %d, %Y')}

## Executive Summary
This report outlines {len(kpi_list)} key performance indicators that should be tracked and monitored for business success.

## KPI Details

"""
    
    # Categorize KPIs if categories are available
    categorized_kpis = {}
    uncategorized_kpis = []
    
    for kpi in kpi_list:
        category = kpi.get('category', '').strip()
        if category and category.lower() != 'general':
            if category not in categorized_kpis:
                categorized_kpis[category] = []
            categorized_kpis[category].append(kpi)
        else:
            uncategorized_kpis.append(kpi)
    
    # Output categorized KPIs
    for category, kpis in categorized_kpis.items():
        report += f"### {category}\n\n"
        for kpi in kpis:
            report += generate_single_kpi_section(kpi)
    
    # Output uncategorized KPIs
    if uncategorized_kpis:
        if categorized_kpis:
            report += "### General Metrics\n\n"
        for kpi in uncategorized_kpis:
            report += generate_single_kpi_section(kpi)
    
    report += """
## Implementation Notes
- These KPIs should be calculated consistently across all reports and dashboards
- Ensure data sources support the required calculations
- Review and update targets regularly based on business performance
- Consider data refresh frequency requirements for real-time vs. batch reporting

## Next Steps
1. Validate KPI definitions with business stakeholders
2. Identify data sources and calculation methods for each metric
3. Establish baseline measurements and target values
4. Create monitoring dashboards and alert thresholds
5. Schedule regular review cycles for KPI relevance and accuracy
"""
    
    return report

def generate_single_kpi_section(kpi):
    """Generate a report section for a single KPI"""
    name = kpi.get('name', 'Unnamed KPI')
    description = kpi.get('description', 'No description provided')
    
    section = f"**{name}**\n"
    section += f"- *Description:* {description}\n"
    
    if kpi.get('calculation'):
        section += f"- *Calculation:* {kpi['calculation']}\n"
    
    if kpi.get('target'):
        section += f"- *Target:* {kpi['target']}\n"
    
    if kpi.get('frequency'):
        section += f"- *Frequency:* {kpi['frequency']}\n"
    
    section += "\n"
    return section

def generate_data_dictionary_summary_text(data_dictionary):
    """Generate a text summary of data dictionary for copy/paste"""
    if not data_dictionary:
        return "No data dictionary defined."
    
    summary = f"# Data Dictionary Summary ({len(data_dictionary)} tables)\n\n"
    
    for table_name, columns in data_dictionary.items():
        summary += f"## {table_name} ({len(columns)} fields)\n\n"
        for col_name, col_info in columns.items():
            description = col_info.get('description', 'No description')
            data_type = col_info.get('data_type', 'Unknown')
            summary += f"- **{col_name}** ({data_type}): {description}\n"
        summary += "\n"
    
    return summary

def generate_data_dictionary_business_report(data_dictionary):
    """Generate a comprehensive business report for data dictionary"""
    if not data_dictionary:
        return "No data dictionary available for report generation."
    
    report = f"""# Data Dictionary Report
Generated on: {datetime.now().strftime('%B %d, %Y')}

## Overview
This report provides comprehensive documentation for all data fields across {len(data_dictionary)} tables in the data model.

## Table Details

"""
    
    for table_name, columns in data_dictionary.items():
        report += f"### {table_name}\n\n"
        report += f"**Total Fields:** {len(columns)}\n\n"
        
        # Categorize columns by type
        key_cols = []
        date_cols = []
        numeric_cols = []
        text_cols = []
        
        for col_name, col_info in columns.items():
            data_type = col_info.get('data_type', '').lower()
            if 'id' in col_name.lower() or 'key' in col_name.lower():
                key_cols.append(col_info)
            elif any(dt in data_type for dt in ['date', 'time', 'timestamp']):
                date_cols.append(col_info)
            elif any(dt in data_type for dt in ['int', 'float', 'decimal', 'number', 'numeric']):
                numeric_cols.append(col_info)
            else:
                text_cols.append(col_info)
        
        if key_cols:
            report += "**🔑 Key Fields:**\n"
            for col in key_cols:
                col_name = col.get("column_name", "")
                col_type = col.get("data_type", "")
                description = col.get("description", "No description")
                report += f"- `{col_name}` ({col_type}) - {description}\n"
        
        if numeric_cols:
            report += "**🔢 Numeric Fields:**\n"
            for col in numeric_cols:
                col_name = col.get("column_name", "")
                col_type = col.get("data_type", "")
                nullable = "nullable" if col.get("nullable", True) else "not null"
                report += f"- `{col_name}` ({col_type}) - {nullable}\n"
        
        if date_cols:
            report += "**📅 Date/Time Columns:**\n"
            for col in date_cols:
                col_name = col.get("column_name", "")
                col_type = col.get("data_type", "")
                nullable = "nullable" if col.get("nullable", True) else "not null"
                report += f"- `{col_name}` ({col_type}) - {nullable}\n"
        
        if text_cols:
            report += "**📝 Text Columns:**\n"
            for col in text_cols:
                if col not in key_cols:  # Avoid duplicates
                    col_name = col.get("column_name", "")
                    col_type = col.get("data_type", "")
                    nullable = "nullable" if col.get("nullable", True) else "not null"
                    report += f"- `{col_name}` ({col_type}) - {nullable}\n"
        
        report += "\n"
        
        # Add any table-level notes
        if any(col_info.get('example') for col_info in columns.values()):
            report += "**Example Values:**\n"
            for col_name, col_info in columns.items():
                if col_info.get('example'):
                    report += f"- {col_name}: {col_info['example']}\n"
            report += "\n"
    
    report += """
## Data Quality Guidelines
- All field descriptions should be kept current with business changes
- Data types should accurately reflect storage and usage requirements
- Business rules should be enforced at the source system level when possible
- Regular reviews should be conducted to ensure dictionary accuracy

## Contact Information
For questions about specific data fields or to suggest updates to this dictionary, please contact your data governance team or business analysts.
"""
    
    return report

def generate_combined_business_summary(kpi_list, data_dictionary):
    """Generate a combined summary of both KPIs and data dictionary"""
    summary = "# Business Context Summary\n\n"
    
    if kpi_list:
        summary += f"## 📊 Key Performance Indicators ({len(kpi_list)} metrics)\n\n"
        for i, kpi in enumerate(kpi_list[:10], 1):  # Limit to 10 for summary
            name = kpi.get('name', f'KPI {i}')
            description = kpi.get('description', 'No description')
            summary += f"**{i}. {name}:** {description}\n"
        
        if len(kpi_list) > 10:
            summary += f"... and {len(kpi_list) - 10} more KPIs\n"
        summary += "\n"
    
    if data_dictionary:
        total_tables = len(data_dictionary)
        total_columns = sum(len(columns) for columns in data_dictionary.values())
        
        summary += f"## 📖 Data Dictionary ({total_tables} tables, {total_columns} fields)\n\n"
        
        for table_name, columns in list(data_dictionary.items())[:5]:  # Limit to 5 tables
            summary += f"**{table_name}** ({len(columns)} fields)\n"
            # Show key fields
            for col_name, col_info in list(columns.items())[:3]:
                summary += f"   • {col_name}: {col_info.get('description', 'No description')}\n"
        
        if total_tables > 5:
            summary += f"... and {total_tables - 5} more tables\n"
    
    return summary

def generate_combined_business_report(kpi_list, data_dictionary, model_metadata):
    """Generate a complete business report combining KPIs, data dictionary, and model info"""
    
    report = f"""# Complete Business Context Report
Generated on: {datetime.now().strftime('%B %d, %Y')}

## Executive Summary
This comprehensive report provides complete business context for dashboard development and data analysis projects.

"""
    
    # Add model overview if available
    if model_metadata:
        model_dict = safe_get_dict(model_metadata)
        tables = safe_get_list(model_dict.get("tables", []))
        relationships = safe_get_list(model_dict.get("relationships", []))
        
        report += f"""## 🏗️ Data Model Overview
- **Tables:** {len(tables)}
- **Relationships:** {len(relationships)}
- **Complexity:** {analyze_model_complexity(model_metadata)}

"""
    
    # Add KPI section
    if kpi_list:
        report += f"## 📊 Key Performance Indicators\n"
        report += f"Total KPIs defined: {len(kpi_list)}\n\n"
        report += generate_kpi_business_report(kpi_list)
    
    # Add data dictionary section
    if data_dictionary:
        report += f"\n## 📖 Data Dictionary\n"
        total_tables = len(data_dictionary)
        total_columns = sum(len(columns) for columns in data_dictionary.values())
        report += f"Total tables: {total_tables}, Total fields: {total_columns}\n\n"
        report += generate_data_dictionary_business_report(data_dictionary)
    
    # Add implementation recommendations
    report += f"""

## 🚀 Implementation Recommendations

### Dashboard Development Priorities
1. **Start with Core KPIs**: Focus on the most critical business metrics first
2. **Establish Data Quality**: Ensure reliable data sources for key calculations
3. **Design for Users**: Create intuitive interfaces that match user workflows
4. **Plan for Scale**: Consider performance implications as data volume grows

### Data Governance
- Establish clear ownership for each KPI and data field
- Create processes for updating definitions as business needs evolve
- Implement data quality monitoring for critical metrics
- Document any transformations or calculations applied to source data

### Success Metrics
- User adoption rates for dashboard solutions
- Accuracy of KPI calculations vs. manual processes
- Time savings in report generation and analysis
- Business decision speed improvements

## Next Steps
1. Review and approve all KPI definitions with business stakeholders
2. Validate data dictionary against current source systems
3. Create development roadmap prioritizing high-impact metrics
4. Establish regular review cycles for maintaining business context accuracy
"""
    
    return report