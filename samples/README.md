# Sample Data Directory

This directory contains sample API responses for validation testing.

## Directory Structure

```
samples/
├── soap/
│   ├── uat-approved/     # UAT-approved SOAP XML responses (baseline)
│   └── prod-actual/      # PROD SOAP XML responses to validate
└── rest/
    ├── uat-approved/     # UAT-approved REST JSON responses (baseline)
    └── prod-actual/      # PROD REST JSON responses to validate
```

## File Naming Conventions

### SOAP Files
- **UAT-approved**: `{ResponseType}-approved.xml`
  - Example: `R0001-approved.xml`, `GETCONTACTQA_213-approved.xml`
- **PROD actual**: `{ResponseType}-actual.xml`
  - Example: `R0001-actual.xml`, `GETCONTACTQA_213-actual.xml`

### REST Files
- **UAT-approved**: `{endpoint}-approved.json`
  - Example: `users-approved.json`, `GETQAMETADA-approved.json`
- **PROD actual**: `{endpoint}-actual.json`
  - Example: `users-actual.json`, `GETQAMETADA-actual.json`

## Usage

1. Place your UAT-approved responses in the appropriate `uat-approved/` directory
2. Place your PROD responses in the appropriate `prod-actual/` directory
3. Ensure file names match the naming convention
4. Run the validation tools to compare PROD against UAT baseline

## Notes

- UAT-approved files serve as the "source of truth" contract
- PROD files are validated against schemas generated from UAT files
- File pairs must have matching base names for automatic discovery
