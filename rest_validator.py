#!/usr/bin/env python3
"""
REST Contract Validation System - Command Line Interface

This tool validates PROD REST responses against UAT-approved contracts by:
1. Generating JSON schemas from UAT responses
2. Validating PROD responses against those schemas
3. Producing HTML reports showing compliance status
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
import jsonschema
from jsonschema import Draft7Validator, ValidationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: Path) -> Dict[Any, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Failed to read {file_path}: {e}")


def generate_json_schema(json_data: Dict[Any, Any], endpoint_name: str) -> Dict[Any, Any]:
    """
    Generate a JSON Schema from a JSON document.
    
    This creates a permissive schema that validates structure while allowing
    flexibility in values.
    """
    def infer_schema(obj, path="root"):
        """Recursively infer JSON Schema from a JSON object."""
        if obj is None:
            return {"type": "null"}
        elif isinstance(obj, bool):
            return {"type": "boolean"}
        elif isinstance(obj, int):
            return {"type": "integer"}
        elif isinstance(obj, float):
            return {"type": "number"}
        elif isinstance(obj, str):
            return {"type": "string"}
        elif isinstance(obj, list):
            if not obj:
                # Empty array - allow any items
                return {
                    "type": "array",
                    "items": {}
                }
            # Infer schema from first item (assuming homogeneous array)
            item_schema = infer_schema(obj[0], f"{path}[]")
            return {
                "type": "array",
                "items": item_schema
            }
        elif isinstance(obj, dict):
            properties = {}
            required = []
            for key, value in obj.items():
                properties[key] = infer_schema(value, f"{path}.{key}")
                # Make all fields required by default
                required.append(key)
            
            schema = {
                "type": "object",
                "properties": properties
            }
            if required:
                schema["required"] = required
            
            # Allow additional properties for flexibility
            schema["additionalProperties"] = True
            
            return schema
        else:
            return {}
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": f"{endpoint_name} Response Schema",
        "description": f"JSON Schema generated from UAT-approved response for {endpoint_name}",
        **infer_schema(json_data)
    }
    
    return schema


def validate_json_against_schema(json_data: Dict[Any, Any], schema: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """
    Validate JSON data against a JSON Schema.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = Draft7Validator(schema)
    errors = []
    
    for error in validator.iter_errors(json_data):
        # Format error message with path
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"{path}: {error.message}")
    
    return len(errors) == 0, errors


def generate_html_report(is_valid: bool, violations: List[str], metadata: Dict[str, Any]) -> str:
    """Generate HTML report content."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REST Contract Validation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: {'#4CAF50' if is_valid else '#f44336'};
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .status {{
            font-size: 24px;
            font-weight: bold;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #666;
        }}
        .violation {{
            background-color: #ffebee;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #f44336;
            border-radius: 3px;
        }}
        .path {{
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="status">{'✓ VALIDATION PASSED' if is_valid else '✗ VALIDATION FAILED'}</div>
        <p>PROD response {'conforms to' if is_valid else 'violates'} UAT-approved contract</p>
    </div>
    
    <div class="section">
        <h2>Validation Summary</h2>
        <div class="metadata">
            <div class="metadata-label">Status:</div>
            <div>{'PASS' if is_valid else 'FAIL'}</div>
            
            <div class="metadata-label">Endpoint:</div>
            <div>{metadata.get('endpoint', 'N/A')}</div>
            
            <div class="metadata-label">UAT Response:</div>
            <div>{metadata.get('uat_file', 'N/A')}</div>
            
            <div class="metadata-label">PROD Response:</div>
            <div>{metadata.get('prod_file', 'N/A')}</div>
            
            <div class="metadata-label">Schema:</div>
            <div>{metadata.get('schema_file', 'N/A')}</div>
            
            <div class="metadata-label">Timestamp:</div>
            <div>{metadata.get('timestamp', 'N/A')}</div>
            
            <div class="metadata-label">System Version:</div>
            <div>0.1.0</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Contract Violations ({len(violations)})</h2>
        {'<p>No contract violations found. PROD response structure matches UAT schema.</p>' if not violations else ''}
        {''.join([f'<div class="violation"><strong>Violation:</strong> {v}</div>' for v in violations])}
    </div>
</body>
</html>"""


def generate_schema_command(args):
    """Generate JSON schema from UAT-approved REST response."""
    logger.info(f"Generating schema from: {args.uat_file}")
    
    try:
        uat_file = Path(args.uat_file)
        
        # Load UAT response
        uat_data = load_json_file(uat_file)
        logger.info("✓ Parsed UAT response")
        
        # Extract endpoint name from filename
        endpoint_name = uat_file.stem.replace("-approved", "")
        
        # Generate schema
        schema = generate_json_schema(uat_data, endpoint_name)
        logger.info(f"✓ Generated schema for endpoint: {endpoint_name}")
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(args.schema_dir) / f"{endpoint_name}-schema.json"
        
        # Save schema
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        
        logger.info(f"✓ Saved schema to: {output_path}")
        
        print(f"\nSuccess! Schema saved to: {output_path}")
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return 1


def validate_command(args):
    """Validate PROD response against JSON schema."""
    logger.info(f"Validating: {args.prod_file}")
    
    try:
        prod_file = Path(args.prod_file)
        
        # Load PROD response
        prod_data = load_json_file(prod_file)
        logger.info("✓ Parsed PROD response")
        
        # Extract endpoint name
        endpoint_name = prod_file.stem.replace("-actual", "")
        logger.info(f"✓ Endpoint: {endpoint_name}")
        
        # Load schema
        schema_path = Path(args.schema_dir) / f"{endpoint_name}-schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        schema = load_json_file(schema_path)
        logger.info(f"✓ Loaded schema: {schema_path}")
        
        # Validate
        is_valid, errors = validate_json_against_schema(prod_data, schema)
        
        if is_valid:
            logger.info("✓ Validation PASSED")
            print("\n✓ VALIDATION PASSED")
            print("PROD response conforms to UAT-approved contract")
            return 0
        else:
            logger.warning(f"✗ Validation FAILED with {len(errors)} error(s)")
            print("\n✗ VALIDATION FAILED")
            print(f"Found {len(errors)} violation(s):")
            for i, error in enumerate(errors[:10], 1):
                print(f"  {i}. {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
            return 1
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return 1


def full_workflow_command(args):
    """Run complete validation workflow: generate schema, validate, and create report."""
    logger.info("Starting full validation workflow")
    
    try:
        uat_file = Path(args.uat_file)
        prod_file = Path(args.prod_file)
        schema_dir = Path(args.schema_dir)
        report_file = Path(args.output) if args.output else Path("reports/rest/validation-report.html")
        
        # Extract endpoint name
        endpoint_name = uat_file.stem.replace("-approved", "")
        
        # Step 1: Generate schema
        logger.info("Step 1: Generating schema from UAT response")
        uat_data = load_json_file(uat_file)
        schema = generate_json_schema(uat_data, endpoint_name)
        schema_path = schema_dir / f"{endpoint_name}-schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        logger.info(f"✓ Schema saved: {schema_path}")
        
        # Step 2: Validate PROD response
        logger.info("Step 2: Validating PROD response")
        prod_data = load_json_file(prod_file)
        is_valid, violations = validate_json_against_schema(prod_data, schema)
        
        if is_valid:
            logger.info("✓ Validation PASSED")
        else:
            logger.warning(f"✗ Validation FAILED with {len(violations)} violation(s)")
        
        # Step 3: Generate report
        logger.info("Step 3: Generating HTML report")
        metadata = {
            'endpoint': endpoint_name,
            'uat_file': str(uat_file),
            'prod_file': str(prod_file),
            'schema_file': str(schema_path),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        html_content = generate_html_report(is_valid, violations, metadata)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(html_content, encoding='utf-8')
        logger.info(f"✓ Report saved: {report_file}")
        
        print("\n" + "=" * 80)
        print("VALIDATION WORKFLOW COMPLETE")
        print("=" * 80)
        print(f"\nStatus: {'✓ PASSED' if is_valid else '✗ FAILED'}")
        print(f"Endpoint: {endpoint_name}")
        print(f"Schema: {schema_path}")
        print(f"Report: {report_file}")
        print(f"\nOpen report: file://{report_file.absolute()}")
        
        return 0 if is_valid else 1
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="REST Contract Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate schema from UAT response
  %(prog)s generate-schema samples/rest/uat-approved/users-approved.json
  
  # Validate PROD response
  %(prog)s validate samples/rest/prod-actual/users-actual.json
  
  # Run full workflow
  %(prog)s full-workflow samples/rest/uat-approved/users-approved.json samples/rest/prod-actual/users-actual.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate schema command
    gen_parser = subparsers.add_parser('generate-schema', help='Generate JSON schema from UAT response')
    gen_parser.add_argument('uat_file', help='Path to UAT-approved REST response JSON file')
    gen_parser.add_argument('--output', '-o', help='Output path for schema file')
    gen_parser.add_argument('--schema-dir', default='contracts/rest', help='Directory for schema files (default: contracts/rest)')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate PROD response against schema')
    val_parser.add_argument('prod_file', help='Path to PROD REST response JSON file')
    val_parser.add_argument('--schema-dir', default='contracts/rest', help='Directory containing schema files (default: contracts/rest)')
    
    # Full workflow command
    full_parser = subparsers.add_parser('full-workflow', help='Run complete validation workflow')
    full_parser.add_argument('uat_file', help='Path to UAT-approved REST response JSON file')
    full_parser.add_argument('prod_file', help='Path to PROD REST response JSON file')
    full_parser.add_argument('--output', '-o', help='Output path for HTML report')
    full_parser.add_argument('--schema-dir', default='contracts/rest', help='Directory for schema files (default: contracts/rest)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'generate-schema':
        return generate_schema_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    elif args.command == 'full-workflow':
        return full_workflow_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
