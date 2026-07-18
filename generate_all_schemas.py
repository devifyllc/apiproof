#!/usr/bin/env python3
"""
Generate XSD schemas for all UAT-approved SOAP responses.

This script discovers all UAT-approved files and generates corresponding
XSD schemas in the contracts/soap/ directory.
"""

import sys
from pathlib import Path
from src.xml_parser import XMLParser
from src.schema_generator import SchemaGenerator
from src.exceptions import XMLParseError, SchemaGenerationError, ResponseTypeNotFoundError


def main():
    print("=" * 80)
    print("SOAP Schema Generator - Batch Processing")
    print("=" * 80)
    print()
    
    # Setup paths
    uat_dir = Path("samples/soap/uat-approved")
    schema_dir = Path("contracts/soap")
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all UAT-approved files
    uat_files = sorted(uat_dir.glob("*-approved.xml"))
    
    if not uat_files:
        print("❌ No UAT-approved files found in samples/soap/uat-approved/")
        return 1
    
    print(f"🔍 Found {len(uat_files)} UAT-approved file(s)")
    print()
    
    # Initialize components
    parser = XMLParser()
    generator = SchemaGenerator()
    
    # Track results
    success_count = 0
    error_count = 0
    skipped_count = 0
    results = []
    
    # Process each UAT file
    for i, uat_file in enumerate(uat_files, 1):
        base_name = uat_file.stem.replace("-approved", "")
        print(f"[{i}/{len(uat_files)}] Processing: {base_name}")
        
        try:
            # Parse UAT response
            uat_doc = parser.parse_file(uat_file)
            
            # Generate schema
            schema = generator.generate_schema(uat_doc)
            
            # Determine output path
            schema_path = schema_dir / f"{schema.response_type}-schema.xsd"
            
            # Check if schema already exists
            if schema_path.exists():
                print(f"   ⏭️  Schema already exists: {schema_path.name}")
                skipped_count += 1
                results.append({
                    'name': base_name,
                    'status': 'SKIPPED',
                    'schema': schema_path,
                    'error': None
                })
                continue
            
            # Save schema
            generator.save_schema(schema, schema_path)
            
            print(f"   ✅ Generated: {schema_path.name}")
            success_count += 1
            results.append({
                'name': base_name,
                'status': 'SUCCESS',
                'schema': schema_path,
                'error': None
            })
            
        except ResponseTypeNotFoundError as e:
            print(f"   ⚠️  Could not extract response type: {e}")
            error_count += 1
            results.append({
                'name': base_name,
                'status': 'ERROR',
                'schema': None,
                'error': str(e)
            })
            
        except (XMLParseError, SchemaGenerationError) as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
            results.append({
                'name': base_name,
                'status': 'ERROR',
                'schema': None,
                'error': str(e)
            })
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            error_count += 1
            results.append({
                'name': base_name,
                'status': 'ERROR',
                'schema': None,
                'error': str(e)
            })
        
        print()
    
    # Print summary
    print("=" * 80)
    print("SCHEMA GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total files:     {len(uat_files)}")
    print(f"Generated:       {success_count} ✅")
    print(f"Already existed: {skipped_count} ⏭️")
    print(f"Errors:          {error_count} ❌")
    print()
    
    # List generated schemas
    if success_count > 0:
        print("📁 Generated schemas:")
        for result in results:
            if result['status'] == 'SUCCESS':
                print(f"   • {result['schema'].name}")
        print()
    
    # List errors if any
    if error_count > 0:
        print("⚠️  Files with errors:")
        for result in results:
            if result['status'] == 'ERROR':
                print(f"   • {result['name']}: {result['error']}")
        print()
    
    print(f"📂 Schemas directory: {schema_dir.absolute()}")
    print()
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
