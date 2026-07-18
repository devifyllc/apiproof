#!/usr/bin/env python3
"""
SOAP Contract Validation System - Command Line Interface

This tool validates PROD SOAP responses against UAT-approved contracts by:
1. Generating XSD schemas from UAT responses
2. Validating PROD responses against those schemas
3. Producing HTML reports showing compliance status
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

from src.xml_parser import XMLParser
from src.schema_generator import SchemaGenerator
from src.models import (
    XSDSchema, ValidationResult, ContractViolation, ViolationType,
    ValueDifference, DifferenceType, ReportMetadata, HTMLReport
)
from src.exceptions import (
    SOAPValidationError, XMLParseError, SchemaGenerationError,
    SchemaNotFoundError, ResponseTypeNotFoundError
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_schema_command(args):
    """Generate XSD schema from UAT-approved SOAP response."""
    logger.info(f"Generating schema from: {args.uat_file}")
    
    try:
        parser = XMLParser()
        generator = SchemaGenerator()
        
        # Parse UAT response
        uat_doc = parser.parse_file(Path(args.uat_file))
        logger.info("✓ Parsed UAT response")
        
        # Generate schema
        schema = generator.generate_schema(uat_doc)
        logger.info(f"✓ Generated schema for response type: {schema.response_type}")
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(args.schema_dir) / f"{schema.response_type}-schema.xsd"
        
        # Save schema
        generator.save_schema(schema, output_path)
        logger.info(f"✓ Saved schema to: {output_path}")
        
        print(f"\nSuccess! Schema saved to: {output_path}")
        return 0
        
    except (XMLParseError, SchemaGenerationError, ResponseTypeNotFoundError) as e:
        logger.error(f"✗ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return 1


def validate_command(args):
    """Validate PROD response against XSD schema."""
    logger.info(f"Validating: {args.prod_file}")
    
    try:
        parser = XMLParser()
        generator = SchemaGenerator()
        
        # Parse PROD response
        prod_doc = parser.parse_file(Path(args.prod_file))
        logger.info("✓ Parsed PROD response")
        
        # Extract response type
        response_type = generator.extract_response_type(prod_doc)
        logger.info(f"✓ Response type: {response_type}")
        
        # Load schema
        schema_path = Path(args.schema_dir) / f"{response_type}-schema.xsd"
        if not schema_path.exists():
            raise SchemaNotFoundError(f"Schema not found: {schema_path}")
        
        schema_content = schema_path.read_text()
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=prod_doc.root.namespace,
            response_type=response_type
        )
        logger.info(f"✓ Loaded schema: {schema_path}")
        
        # Validate
        validation_errors = schema.validate_document(prod_doc)
        
        if not validation_errors:
            logger.info("✓ Validation PASSED")
            print("\n✓ VALIDATION PASSED")
            print("PROD response conforms to UAT-approved contract")
            return 0
        else:
            logger.warning(f"✗ Validation FAILED with {len(validation_errors)} error(s)")
            print("\n✗ VALIDATION FAILED")
            print(f"Found {len(validation_errors)} violation(s):")
            for i, error in enumerate(validation_errors[:10], 1):
                print(f"  {i}. {error}")
            if len(validation_errors) > 10:
                print(f"  ... and {len(validation_errors) - 10} more")
            return 1
        
    except (XMLParseError, SchemaNotFoundError, ResponseTypeNotFoundError) as e:
        logger.error(f"✗ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def full_workflow_command(args):
    """Run complete validation workflow: generate schema, validate, and create report."""
    logger.info("Starting full validation workflow")
    
    try:
        parser = XMLParser()
        generator = SchemaGenerator()
        
        uat_file = Path(args.uat_file)
        prod_file = Path(args.prod_file)
        schema_dir = Path(args.schema_dir)
        report_file = Path(args.output) if args.output else Path("reports/soap/prod-vs-uat-contract-report.html")
        
        # Step 1: Generate schema
        logger.info("Step 1: Generating schema from UAT response")
        uat_doc = parser.parse_file(uat_file)
        schema = generator.generate_schema(uat_doc)
        schema_path = schema_dir / f"{schema.response_type}-schema.xsd"
        generator.save_schema(schema, schema_path)
        logger.info(f"✓ Schema saved: {schema_path}")
        
        # Step 2: Validate PROD response
        logger.info("Step 2: Validating PROD response")
        prod_doc = parser.parse_file(prod_file)
        
        schema_content = schema_path.read_text()
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=prod_doc.root.namespace,
            response_type=schema.response_type
        )
        
        validation_errors = schema.validate_document(prod_doc)
        
        if not validation_errors:
            is_valid = True
            violations = []
            logger.info("✓ Validation PASSED")
        else:
            is_valid = False
            violations = [
                ContractViolation(
                    violation_type=ViolationType.INVALID_STRUCTURE,
                    element_path="unknown",
                    description=str(error)
                )
                for error in validation_errors
            ]
            logger.warning(f"✗ Validation FAILED with {len(violations)} violation(s)")
        
        validation_result = ValidationResult(
            is_valid=is_valid,
            violations=violations,
            prod_response_path=prod_file,
            schema_path=schema_path,
            timestamp=datetime.now()
        )
        
        # Step 3: Compare values (simplified)
        logger.info("Step 3: Comparing data values")
        value_differences = []
        # TODO: Implement full value comparison
        
        # Step 4: Generate report
        logger.info("Step 4: Generating HTML report")
        metadata = ReportMetadata(
            uat_response_path=uat_file,
            prod_response_path=prod_file,
            schema_path=schema_path,
            validation_timestamp=datetime.now(),
            system_version="0.1.0"
        )
        
        html_content = generate_html_report(validation_result, value_differences, metadata)
        report = HTMLReport(html_content=html_content, metadata=metadata)
        report.save_to_file(report_file)
        logger.info(f"✓ Report saved: {report_file}")
        
        print("\n" + "=" * 80)
        print("VALIDATION WORKFLOW COMPLETE")
        print("=" * 80)
        print(f"\nStatus: {'✓ PASSED' if is_valid else '✗ FAILED'}")
        print(f"Schema: {schema_path}")
        print(f"Report: {report_file}")
        print(f"\nOpen report: file://{report_file.absolute()}")
        
        return 0 if is_valid else 1
        
    except SOAPValidationError as e:
        logger.error(f"✗ Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def generate_html_report(validation_result, value_differences, metadata):
    """Generate HTML report content."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOAP Contract Validation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: {'#4CAF50' if validation_result.is_valid else '#f44336'};
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
        .difference {{
            background-color: #fff3e0;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #ff9800;
            border-radius: 3px;
        }}
        .path {{
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="status">{'✓ VALIDATION PASSED' if validation_result.is_valid else '✗ VALIDATION FAILED'}</div>
        <p>PROD response {'conforms to' if validation_result.is_valid else 'violates'} UAT-approved contract</p>
    </div>
    
    <div class="section">
        <h2>Validation Summary</h2>
        <div class="metadata">
            <div class="metadata-label">Status:</div>
            <div>{'PASS' if validation_result.is_valid else 'FAIL'}</div>
            
            <div class="metadata-label">UAT Response:</div>
            <div>{metadata.uat_response_path}</div>
            
            <div class="metadata-label">PROD Response:</div>
            <div>{metadata.prod_response_path}</div>
            
            <div class="metadata-label">Schema:</div>
            <div>{metadata.schema_path}</div>
            
            <div class="metadata-label">Timestamp:</div>
            <div>{metadata.validation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            
            <div class="metadata-label">System Version:</div>
            <div>{metadata.system_version}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Contract Violations ({len(validation_result.violations)})</h2>
        {'<p>No contract violations found. PROD response structure matches UAT schema.</p>' if not validation_result.violations else ''}
        {''.join([f'<div class="violation"><strong>Violation:</strong> {v.description}</div>' for v in validation_result.violations])}
    </div>
    
    <div class="section">
        <h2>Value Differences ({len(value_differences)})</h2>
        {'<p>No value differences found between UAT and PROD responses.</p>' if not value_differences else ''}
        {''.join([f'<div class="difference"><span class="path">{d.element_path}</span><br>UAT: {d.uat_value}<br>PROD: {d.prod_value}</div>' for d in value_differences])}
    </div>
</body>
</html>"""


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SOAP Contract Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate schema from UAT response
  %(prog)s generate-schema samples/soap/uat-approved/R0001-approved.xml
  
  # Validate PROD response
  %(prog)s validate samples/soap/prod-actual/R0001-actual.xml
  
  # Run full workflow
  %(prog)s full-workflow samples/soap/uat-approved/R0001-approved.xml samples/soap/prod-actual/R0001-actual.xml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate schema command
    gen_parser = subparsers.add_parser('generate-schema', help='Generate XSD schema from UAT response')
    gen_parser.add_argument('uat_file', help='Path to UAT-approved SOAP response XML file')
    gen_parser.add_argument('--output', '-o', help='Output path for schema file')
    gen_parser.add_argument('--schema-dir', default='contracts/soap', help='Directory for schema files (default: contracts/soap)')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate PROD response against schema')
    val_parser.add_argument('prod_file', help='Path to PROD SOAP response XML file')
    val_parser.add_argument('--schema-dir', default='contracts/soap', help='Directory containing schema files (default: contracts/soap)')
    
    # Full workflow command
    full_parser = subparsers.add_parser('full-workflow', help='Run complete validation workflow')
    full_parser.add_argument('uat_file', help='Path to UAT-approved SOAP response XML file')
    full_parser.add_argument('prod_file', help='Path to PROD SOAP response XML file')
    full_parser.add_argument('--output', '-o', help='Output path for HTML report')
    full_parser.add_argument('--schema-dir', default='contracts/soap', help='Directory for schema files (default: contracts/soap)')
    
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
