# APIProof Setup Guide

This guide will help you set up and start using APIProof for API contract validation.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation Steps

### 1. Verify Python Installation

```bash
python3 --version
# Should show Python 3.8 or higher
```

### 2. Create Virtual Environment (Recommended)

```bash
# Navigate to the project directory
cd apiproof

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `lxml` - XML processing and XSD validation
- `xmlschema` - XSD schema generation
- `jsonschema` - JSON schema validation
- `jinja2` - HTML report templating
- `pytest` - Testing framework (optional)

### 4. Verify Installation

```bash
# Check if dependencies are installed
pip list

# Run a simple test (if you have test files)
pytest --version
```

## Project Structure Setup

The following directories are already created:

```
apiproof/
├── src/                    # Core source code ✓
├── tests/                  # Test suite ✓
├── samples/                # Sample API responses
│   ├── soap/
│   │   ├── uat-approved/  # Place UAT SOAP files here
│   │   └── prod-actual/   # Place PROD SOAP files here
│   └── rest/
│       ├── uat-approved/  # Place UAT REST files here
│       └── prod-actual/   # Place PROD REST files here
├── contracts/              # Generated schemas (auto-created)
│   ├── soap/
│   └── rest/
└── reports/                # Generated reports (auto-created)
    ├── soap/
    └── rest/
```

## Quick Start

### SOAP Validation

1. **Place your files**:
   - UAT-approved SOAP response → `samples/soap/uat-approved/R0001-approved.xml`
   - PROD SOAP response → `samples/soap/prod-actual/R0001-actual.xml`

2. **Run validation**:
   ```bash
   python3 soap_validator.py full-workflow \
       samples/soap/uat-approved/R0001-approved.xml \
       samples/soap/prod-actual/R0001-actual.xml
   ```

3. **View report**:
   ```bash
   open reports/soap/prod-vs-uat-contract-report.html
   ```

### REST Validation

1. **Place your files**:
   - UAT-approved REST response → `samples/rest/uat-approved/users-approved.json`
   - PROD REST response → `samples/rest/prod-actual/users-actual.json`

2. **Run validation**:
   ```bash
   python3 rest_validator.py full-workflow \
       samples/rest/uat-approved/users-approved.json \
       samples/rest/prod-actual/users-actual.json
   ```

3. **View report**:
   ```bash
   open reports/rest/validation-report.html
   ```

## Batch Processing

### Validate All SOAP Responses

```bash
python3 validate_all.py
```

This will:
- Discover all UAT/PROD pairs in `samples/soap/`
- Validate each pair
- Generate individual reports
- Create a summary report at `reports/soap/validation-summary.html`

### Validate All REST Endpoints

```bash
python3 validate_rest_all.py
```

This will:
- Discover all UAT/PROD pairs in `samples/rest/`
- Validate each pair
- Generate individual reports
- Create a summary report at `reports/rest/validation-summary.html`

### Generate All SOAP Schemas

```bash
python3 generate_all_schemas.py
```

This will generate XSD schemas for all UAT-approved SOAP responses.

## File Naming Conventions

### SOAP Files
- **UAT**: `{ResponseType}-approved.xml` (e.g., `R0001-approved.xml`)
- **PROD**: `{ResponseType}-actual.xml` (e.g., `R0001-actual.xml`)
- **Schema**: `{ResponseType}-schema.xsd` (auto-generated)

### REST Files
- **UAT**: `{endpoint}-approved.json` (e.g., `users-approved.json`)
- **PROD**: `{endpoint}-actual.json` (e.g., `users-actual.json`)
- **Schema**: `{endpoint}-schema.json` (auto-generated)

## Troubleshooting

### Import Errors

If you see import errors like `ModuleNotFoundError`:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Errors

If scripts are not executable:
```bash
chmod +x soap_validator.py rest_validator.py validate_all.py
```

### XML Parsing Errors

- Ensure XML files are well-formed
- Check for proper namespace declarations
- Verify file encoding is UTF-8

### JSON Validation Errors

- Ensure JSON files are valid
- Check for proper syntax (commas, brackets, quotes)
- Verify file encoding is UTF-8

## Development Setup

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

### Code Quality

The project uses:
- **pytest** for testing
- **pytest-cov** for coverage reporting
- **hypothesis** for property-based testing

Target coverage:
- Line coverage: 90%
- Branch coverage: 85%

## Next Steps

1. ✅ Install dependencies
2. ✅ Verify installation
3. 📁 Add your sample files to `samples/` directories
4. 🚀 Run your first validation
5. 📊 Review the HTML reports
6. 🔄 Set up batch processing for multiple endpoints

## Getting Help

- Check the main [README.md](README.md) for detailed usage
- Review sample files in `samples/` directories
- Open an issue if you encounter problems

---

**Ready to validate!** 🚀
