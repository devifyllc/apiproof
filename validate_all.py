#!/usr/bin/env python3
"""
Batch validation script for multiple SOAP response types.

This script automatically discovers all UAT-approved and PROD-actual response pairs
and runs validation for each one, generating individual reports.
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess

def find_response_pairs():
    """Find all matching UAT-approved and PROD-actual response pairs."""
    uat_dir = Path("samples/soap/uat-approved")
    prod_dir = Path("samples/soap/prod-actual")
    
    pairs = []
    
    # Find all UAT-approved files
    for uat_file in sorted(uat_dir.glob("*-approved.xml")):
        # Extract base name (e.g., "R0001" from "R0001-approved.xml")
        base_name = uat_file.stem.replace("-approved", "")
        
        # Look for corresponding PROD file
        prod_file = prod_dir / f"{base_name}-actual.xml"
        
        if prod_file.exists():
            pairs.append({
                'name': base_name,
                'uat': uat_file,
                'prod': prod_file
            })
        else:
            print(f"⚠️  Warning: No PROD file found for {base_name}")
    
    return pairs


def run_validation(pair, output_dir):
    """Run validation for a single response pair."""
    name = pair['name']
    uat_file = pair['uat']
    prod_file = pair['prod']
    
    # Create output path for this response type
    report_file = output_dir / "soap" / f"{name}-validation-report.html"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"Validating: {name}")
    print(f"{'='*80}")
    print(f"UAT:  {uat_file}")
    print(f"PROD: {prod_file}")
    print()
    
    # Run the validation command
    cmd = [
        "python3", "soap_validator.py", "full-workflow",
        str(uat_file),
        str(prod_file),
        "--output", str(report_file)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Extract validation status from the generated report file
        validation_status = "UNKNOWN"
        if report_file.exists():
            try:
                report_content = report_file.read_text(encoding='utf-8')
                if "✓ VALIDATION PASSED" in report_content or ">✓ VALIDATION PASSED<" in report_content:
                    validation_status = "PASSED"
                elif "✗ VALIDATION FAILED" in report_content or ">✗ VALIDATION FAILED<" in report_content:
                    validation_status = "FAILED"
            except Exception:
                # If we can't read the report, try to extract from stdout
                if "✓ Validation PASSED" in result.stdout or "✓ VALIDATION PASSED" in result.stdout:
                    validation_status = "PASSED"
                elif "✗ Validation FAILED" in result.stdout or "✗ VALIDATION FAILED" in result.stdout:
                    validation_status = "FAILED"
        
        return {
            'name': name,
            'status': validation_status,
            'report': report_file,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout: Validation took too long")
        return {
            'name': name,
            'status': 'TIMEOUT',
            'report': None,
            'success': False,
            'output': '',
            'error': 'Validation timeout'
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            'name': name,
            'status': 'ERROR',
            'report': None,
            'success': False,
            'output': '',
            'error': str(e)
        }


def generate_summary_report(results, output_dir):
    """Generate a summary HTML report for all validations."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] in ['ERROR', 'TIMEOUT'])
    total = len(results)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOAP Contract Validation - Summary Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 32px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .passed {{ color: #4CAF50; }}
        .failed {{ color: #f44336; }}
        .errors {{ color: #ff9800; }}
        .total {{ color: #2196F3; }}
        
        .results-table {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background-color: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
        }}
        .status-passed {{
            background-color: #e8f5e9;
            color: #2e7d32;
        }}
        .status-failed {{
            background-color: #ffebee;
            color: #c62828;
        }}
        .status-error {{
            background-color: #fff3e0;
            color: #e65100;
        }}
        .report-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .report-link:hover {{
            text-decoration: underline;
        }}
        .timestamp {{
            color: #999;
            font-size: 14px;
            margin-top: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 SOAP Contract Validation Summary</h1>
        <p>Batch validation results for all SOAP response types</p>
        <p style="margin: 0; opacity: 0.9;">Generated: {timestamp}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-label">Total Validations</div>
            <div class="stat-number total">{total}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Passed</div>
            <div class="stat-number passed">{passed}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Failed</div>
            <div class="stat-number failed">{failed}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Errors</div>
            <div class="stat-number errors">{errors}</div>
        </div>
    </div>
    
    <div class="results-table">
        <table>
            <thead>
                <tr>
                    <th>Response Type</th>
                    <th>Status</th>
                    <th>Report</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for result in results:
        status_class = {
            'PASSED': 'status-passed',
            'FAILED': 'status-failed',
            'ERROR': 'status-error',
            'TIMEOUT': 'status-error'
        }.get(result['status'], 'status-error')
        
        status_text = {
            'PASSED': '✅ PASSED',
            'FAILED': '❌ FAILED',
            'ERROR': '⚠️ ERROR',
            'TIMEOUT': '⏱️ TIMEOUT'
        }.get(result['status'], '❓ UNKNOWN')
        
        report_link = ''
        if result['report'] and result['report'].exists():
            report_link = f'<a href="{result["report"].name}" class="report-link">View Report →</a>'
        else:
            report_link = '<span style="color: #999;">No report</span>'
        
        html += f"""
                <tr>
                    <td><strong>{result['name']}</strong></td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                    <td>{report_link}</td>
                </tr>
"""
    
    html += f"""
            </tbody>
        </table>
    </div>
    
    <div class="timestamp">
        SOAP Contract Validation System v0.1.0
    </div>
</body>
</html>"""
    
    summary_file = output_dir / "soap" / "validation-summary.html"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(html, encoding='utf-8')
    return summary_file


def main():
    print("=" * 80)
    print("SOAP Contract Validation - Batch Processing")
    print("=" * 80)
    print()
    
    # Find all response pairs
    print("🔍 Discovering SOAP response pairs...")
    pairs = find_response_pairs()
    
    if not pairs:
        print("❌ No response pairs found!")
        return 1
    
    print(f"✅ Found {len(pairs)} response pair(s):")
    for pair in pairs:
        print(f"   • {pair['name']}")
    print()
    
    # Create output directory
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    
    # Run validation for each pair
    results = []
    for i, pair in enumerate(pairs, 1):
        print(f"\n[{i}/{len(pairs)}] Processing {pair['name']}...")
        result = run_validation(pair, output_dir)
        results.append(result)
        
        # Print result
        if result['success']:
            print(f"✅ {pair['name']}: {result['status']}")
        else:
            print(f"❌ {pair['name']}: {result['status']}")
            if result['error']:
                print(f"   Error: {result['error']}")
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("Generating summary report...")
    summary_file = generate_summary_report(results, output_dir)
    print(f"✅ Summary report: {summary_file}")
    
    # Print final summary
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] in ['ERROR', 'TIMEOUT'])
    
    print("\n" + "=" * 80)
    print("BATCH VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Total:  {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Errors: {errors} ⚠️")
    print()
    print(f"📊 Summary report: file://{summary_file.absolute()}")
    print(f"📁 Individual reports: {output_dir}/")
    print()
    
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
