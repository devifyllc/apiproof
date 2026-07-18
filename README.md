# APIProof

**Version 0.1.0**

A Python-based API contract validation system that ensures Production API responses comply with UAT-approved contracts. Validates both SOAP (XML) and REST (JSON) APIs by generating schemas from UAT responses and detecting contract violations in Production environments.

## Purpose

APIProof provides QA and engineering teams with an automated solution to validate API contract compliance across environments. The system treats UAT-approved responses as the signed-off baseline contract and validates Production responses against this baseline to detect structural violations and ensure environment consistency.

Key Features:
- 🔄 **Dual Protocol Support** - Validates both SOAP (XML) and REST (JSON) APIs
- 📋 **Schema Generation** - Automatically generates XSD and JSON schemas from UAT responses
- ✅ **Contract Validation** - Validates PROD responses against generated schemas
- 📊 **HTML Reports** - Produces detailed HTML reports showing validation results and violations
- ⚡ **Batch Processing** - Process multiple endpoints/response types in one command
- 🔍 **Value Difference Detection** - Distinguishes between structural violations and data value differences

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for full terms.

Copyright 2024–2025 Devify LLC

## Requirements

- Python 3.8 or higher (recommended: 3.10+)
- pip 20.x or higher

### Dependencies

- lxml 4.9.0+ - XML processing and XSD validation
- xmlschema 2.0.0+ - XSD schema generation
- jsonschema 4.0.0+ - JSON schema validation
- jinja2 3.1.0+ - HTML report templating
- pytest 7.0.0+ (optional, for testing)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/devifyllc/apiproof.git
cd apiproof
```

2. **Create a virtual environment** (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Running the Project

### SOAP Validation

**Single Validation:**
```bash
# Run full SOAP validation workflow
python3 soap_validator.py full-workflow \
    samples/soap/uat-approved/ADDRESS_FIELDS-approved.xml \
    samples/soap/prod-actual/ADDRESS_FIELDS-actual.xml
```

**Batch Validation:**
```bash
# Validate all SOAP response pairs
python3 validate_all.py
```

**View Reports:**
```bash
# Open the generated report
open reports/soap/ADDRESS_FIELDS-validation-report.html
```

### REST Validation

**Single Validation:**
```bash
# Run full REST validation workflow
python3 rest_validator.py full-workflow \
    samples/rest/uat-approved/ADDRESS_FIELDS-approved.json \
    samples/rest/prod-actual/ADDRESS_FIELDS-actual.json
```

**Batch Validation:**
```bash
# Validate all REST endpoint pairs
python3 validate_rest_all.py
```

**View Reports:**
```bash
# Open the generated report
open reports/rest/ADDRESS_FIELDS-validation-report.html
```

### Verification

Run the installation verification script:
```bash
python3 verify_installation.py
```

## Project Structure

```
apiproof/
├── src/                          # Core source code
│   ├── __init__.py              # Package initialization
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── models.py                # Data models and structures
│   ├── xml_parser.py            # XML parsing utilities
│   ├── schema_generator.py      # Schema generation logic
│   └── pretty_printer.py        # XML formatting utilities
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_exceptions.py
│   ├── test_models.py
│   ├── test_schema_generator.py
│   └── test_xml_parser.py
├── samples/                     # Sample API responses
│   ├── soap/
│   │   ├── uat-approved/        # UAT-approved SOAP responses
│   │   └── prod-actual/         # PROD SOAP responses to validate
│   └── rest/
│       ├── uat-approved/        # UAT-approved REST responses
│       └── prod-actual/         # PROD REST responses to validate
├── contracts/                   # Generated schemas
│   ├── soap/                    # XSD schemas
│   └── rest/                    # JSON schemas
├── reports/                     # Generated HTML reports
│   ├── soap/                    # SOAP validation reports
│   └── rest/                    # REST validation reports
├── soap_validator.py            # SOAP validation CLI
├── rest_validator.py            # REST validation CLI
├── validate_all.py              # Batch SOAP validation
├── validate_rest_all.py         # Batch REST validation
├── generate_all_schemas.py      # Batch schema generation
├── verify_installation.py       # Installation verification
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Package configuration
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

## How It Works

### Validation Workflow

1. **Schema Generation**: Parse UAT-approved response and generate a formal schema (XSD for SOAP, JSON Schema for REST)
2. **Schema Storage**: Save the schema to `contracts/` directory for reuse
3. **PROD Validation**: Parse PROD response and validate against the generated schema
4. **Report Generation**: Create detailed HTML report showing violations and differences

### SOAP Validation Flow

- Parses UAT-approved SOAP XML response
- Generates permissive XSD schema from structure
- Validates PROD SOAP response against XSD schema
- Detects structural violations and data differences

### REST Validation Flow

- Parses UAT-approved JSON response
- Infers JSON Schema from structure and types
- Validates PROD JSON response against JSON Schema
- Detects schema violations and type mismatches

## File Naming Conventions

### SOAP Files
- **UAT-approved**: `{ResponseType}-approved.xml` (e.g., `ADDRESS_FIELDS-approved.xml`)
- **PROD actual**: `{ResponseType}-actual.xml` (e.g., `ADDRESS_FIELDS-actual.xml`)
- **Generated schema**: `{ResponseType}-schema.xsd` (auto-generated)

### REST Files
- **UAT-approved**: `{endpoint}-approved.json` (e.g., `ADDRESS_FIELDS-approved.json`)
- **PROD actual**: `{endpoint}-actual.json` (e.g., `ADDRESS_FIELDS-actual.json`)
- **Generated schema**: `{endpoint}-schema.json` (auto-generated)

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and test thoroughly
4. Run tests: `pytest`
5. Run type checking (if applicable)
6. Commit your changes with clear messages
7. Push to your fork and submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

Built with ❤️ by [Devify LLC](https://github.com/devifyllc)

## About

A Python-based API contract validation system that ensures Production API responses comply with UAT-approved contracts. Validates both SOAP (XML) and REST (JSON) APIs by generating schemas from UAT responses and detecting contract violations in Production environments. Perfect for QA teams ensuring API contract compliance across environments.
