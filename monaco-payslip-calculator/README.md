# Monaco Payslip Calculator Skill

A Claude Code skill for calculating Monaco payslips (bulletin de salaire) with accurate social security contributions.

## Overview

This skill enables Claude to calculate complete Monaco payslips including:
- Gross salary breakdown
- Employee social security contributions (cotisations salariales)
- Net salary calculation
- Employer social security contributions (cotisations patronales)
- Total employer cost
- Formatted payslip output

## Features

- **Accurate Calculations**: Follows Monaco's Caisses Sociales contribution structure
- **Multiple Employee Types**: Supports standard employees and household employees (gens de maison)
- **Flexible Output**: Generate payslips in text or JSON format
- **Command-line Tool**: Standalone Python script for direct calculations
- **Comprehensive Documentation**: Detailed reference for contribution rates and rules

## Installation

1. Upload this skill to Claude Code or your Claude environment
2. The skill will automatically activate when users request Monaco payslip calculations

## Usage

### Through Claude

Simply ask Claude to calculate a Monaco payslip:

```
"Calculate a Monaco payslip for a gross salary of €3,500"
"What would be the employer cost for a €2,800 monthly salary in Monaco?"
"Show me the social security breakdown for a household employee earning €2,000"
```

Claude will:
1. Ask for any missing information (employee type, etc.)
2. Calculate all contributions
3. Present a formatted payslip
4. Explain the calculation

### Direct Script Usage

The calculator can also be used as a standalone command-line tool:

```bash
# Standard employee
python3 scripts/payslip_calculator.py --gross-salary 3500 --employee-type standard

# Household employee with JSON output
python3 scripts/payslip_calculator.py --gross-salary 2500 --employee-type household --output-format json
```

## Structure

```
monaco-payslip-calculator/
├── SKILL.md                          # Main skill instructions for Claude
├── README.md                         # This file
├── scripts/
│   └── payslip_calculator.py        # Python calculation engine
├── references/
│   └── contribution_rates.md        # Detailed contribution rate documentation
└── assets/
    ├── payslip_template.txt         # Formatted payslip template
    └── example_payslips/            # Example calculations
        ├── example_standard_3500.txt
        ├── example_standard_3500.json
        └── example_household_2500.txt
```

## Contribution Categories

### Employee Contributions (Deducted from gross salary)
- **Maladie**: Health insurance
- **Vieillesse**: Pension/retirement
- **Chômage**: Unemployment

### Employer Contributions (Added to employer cost)
- **Maladie**: Health insurance (employer portion)
- **Vieillesse**: Pension/retirement (employer portion)
- **Chômage**: Unemployment (employer portion)
- **Accidents du Travail**: Work accidents insurance
- **Allocations Familiales**: Family allowances
- **Formation Professionnelle**: Professional training

## Example Output

### Text Format
```
============================================================
BULLETIN DE SALAIRE - MONACO
============================================================
Type d'employé: STANDARD
Date de calcul: 2025-10-27

------------------------------------------------------------
SALAIRE ET COTISATIONS SALARIALES
------------------------------------------------------------
Salaire brut mensuel:                3500.00 €

Cotisations salariales:
  - Maladie                              126.00 €
  - Vieillesse                           148.75 €
  - Chomage                               17.50 €
  Total cotisations salariales         292.25 €

SALAIRE NET À PAYER:                  3207.75 €

------------------------------------------------------------
COTISATIONS PATRONALES
------------------------------------------------------------
  - Maladie                              451.50 €
  - Vieillesse                           446.25 €
  - Chomage                               52.50 €
  - Accidents Travail                     70.00 €
  - Allocations Familiales               245.00 €
  - Formation Prof                        17.50 €
  Total cotisations patronales        1282.75 €

COÛT TOTAL EMPLOYEUR:                 4782.75 €
```

### JSON Format
```json
{
  "gross_salary": 3500.0,
  "employee_total": 292.25,
  "net_salary": 3207.75,
  "employer_total": 1282.75,
  "total_employer_cost": 4782.75,
  "employee_contributions": {
    "maladie": 126.0,
    "vieillesse": 148.75,
    "chomage": 17.5
  },
  "employer_contributions": {
    "maladie": 451.5,
    "vieillesse": 446.25,
    "chomage": 52.5,
    "accidents_travail": 70.0,
    "allocations_familiales": 245.0,
    "formation_prof": 17.5
  }
}
```

## Updating Contribution Rates

When Monaco contribution rates change:

1. **Obtain Official Rates**: Get the latest rates from Caisses Sociales de Monaco
2. **Update the Script**: Modify rate constants in `scripts/payslip_calculator.py`:
   - `STANDARD_EMPLOYEE_RATES` (lines 34-38)
   - `STANDARD_EMPLOYER_RATES` (lines 41-48)
   - `HOUSEHOLD_EMPLOYEE_RATES` (lines 51-55)
   - `HOUSEHOLD_EMPLOYER_RATES` (lines 57-63)
3. **Update Documentation**: Complete the template in `references/contribution_rates.md`
4. **Test**: Run the calculator with known values and verify against official results
5. **Document**: Note the effective date and source of the rates

## Limitations

- Tax calculations are not included (Monaco has specific tax rules based on nationality/residency)
- Complex scenarios (expatriates, special regimes) may require additional verification
- Contribution rates must be kept current manually
- Always verify critical calculations with qualified Monaco accountants

## Official Resources

- **Caisses Sociales de Monaco**: https://www.caisses-sociales.mc/
- **Employer Portal**: https://employeur.caisses-sociales.mc/
- **Monaco Government**: https://www.gouv.mc/

## Support

For issues or questions about:
- **This skill**: Check the documentation in `SKILL.md` and `references/contribution_rates.md`
- **Monaco regulations**: Contact Caisses Sociales de Monaco directly
- **Specific payroll situations**: Consult a qualified Monaco payroll specialist

## License

[Add appropriate license information]

## Disclaimer

This skill is provided for informational and computational purposes only. Contribution rates are subject to change by Monaco authorities. Always verify current rates with official sources before making actual payroll calculations. For critical or complex situations, consult with qualified Monaco payroll specialists or accountants.
