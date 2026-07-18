#!/usr/bin/env python3
"""
Verification script for APIProof installation.

This script checks that all required components are properly installed
and the project structure is correct.
"""

import sys
from pathlib import Path


def check_directory_structure():
    """Verify all required directories exist."""
    print("Checking directory structure...")
    
    required_dirs = [
        "src",
        "tests",
        "samples/soap/uat-approved",
        "samples/soap/prod-actual",
        "samples/rest/uat-approved",
        "samples/rest/prod-actual",
        "contracts/soap",
        "contracts/rest",
        "reports/soap",
        "reports/rest",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_source_files():
    """Verify all required source files exist."""
    print("\nChecking source files...")
    
    required_files = [
        "src/__init__.py",
        "src/exceptions.py",
        "src/models.py",
        "src/xml_parser.py",
        "src/schema_generator.py",
        "src/pretty_printer.py",
        "soap_validator.py",
        "rest_validator.py",
        "validate_all.py",
        "validate_rest_all.py",
        "generate_all_schemas.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\nChecking Python dependencies...")
    
    dependencies = [
        "lxml",
        "xmlschema",
        "jsonschema",
        "jinja2",
        "pytest",
    ]
    
    all_installed = True
    for package in dependencies:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def check_executables():
    """Check if validator scripts are executable."""
    print("\nChecking executable permissions...")
    
    scripts = [
        "soap_validator.py",
        "rest_validator.py",
        "validate_all.py",
        "validate_rest_all.py",
        "generate_all_schemas.py",
    ]
    
    all_executable = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            import os
            is_executable = os.access(script_path, os.X_OK)
            if is_executable:
                print(f"  ✓ {script}")
            else:
                print(f"  ⚠ {script} - NOT EXECUTABLE (run: chmod +x {script})")
                all_executable = False
        else:
            print(f"  ✗ {script} - MISSING")
            all_executable = False
    
    return all_executable


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("APIProof Installation Verification")
    print("=" * 80)
    print()
    
    checks = [
        ("Directory Structure", check_directory_structure()),
        ("Source Files", check_source_files()),
        ("Python Dependencies", check_dependencies()),
        ("Executable Scripts", check_executables()),
    ]
    
    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80)
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check_name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! APIProof is ready to use.")
        print("\nNext steps:")
        print("  1. Add sample files to samples/ directories")
        print("  2. Run your first validation")
        print("  3. Check the generated reports")
        print("\nFor help, see README.md or SETUP.md")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo make scripts executable:")
        print("  chmod +x *.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
