#!/usr/bin/env python3
"""
Monaco Payslip Calculator
Calculates employer and employee social security contributions for Monaco payslips.

Usage:
    python3 payslip_calculator.py --gross-salary 3500 --employee-type standard
    python3 payslip_calculator.py --gross-salary 2500 --employee-type household --output-format json
"""

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from datetime import datetime


class MonacoPayslipCalculator:
    """
    Calculator for Monaco payslips (bulletin de salaire).

    Handles calculation of social security contributions according to
    Monaco's Caisses Sociales system.
    """

    # NOTE: These rates are TEMPLATE values and must be updated with current official rates
    # from https://www.caisses-sociales.mc/

    # Standard employee contribution rates (as percentage of gross salary)
    STANDARD_EMPLOYEE_RATES = {
        'maladie': Decimal('3.60'),          # Health insurance (employee portion)
        'vieillesse': Decimal('4.25'),       # Pension (employee portion)
        'chomage': Decimal('0.50'),          # Unemployment (employee portion)
    }

    # Standard employer contribution rates (as percentage of gross salary)
    STANDARD_EMPLOYER_RATES = {
        'maladie': Decimal('12.90'),         # Health insurance (employer portion)
        'vieillesse': Decimal('12.75'),      # Pension (employer portion)
        'chomage': Decimal('1.50'),          # Unemployment (employer portion)
        'accidents_travail': Decimal('2.00'), # Work accidents
        'allocations_familiales': Decimal('7.00'), # Family allowances
        'formation_prof': Decimal('0.50'),   # Professional training
    }

    # Household employee (gens de maison) rates - typically different
    HOUSEHOLD_EMPLOYEE_RATES = {
        'maladie': Decimal('3.60'),
        'vieillesse': Decimal('4.25'),
        'chomage': Decimal('0.50'),
    }

    HOUSEHOLD_EMPLOYER_RATES = {
        'maladie': Decimal('10.50'),
        'vieillesse': Decimal('10.00'),
        'chomage': Decimal('1.00'),
        'accidents_travail': Decimal('1.50'),
        'allocations_familiales': Decimal('5.00'),
    }

    # Salary ceilings (plafonds) if applicable - None means no ceiling
    CONTRIBUTION_CEILINGS = {
        'maladie': None,
        'vieillesse': None,  # May have a ceiling - check official rates
        'chomage': None,
        'accidents_travail': None,
        'allocations_familiales': None,
        'formation_prof': None,
    }

    def __init__(self, gross_salary: float, employee_type: str = 'standard'):
        """
        Initialize the payslip calculator.

        Args:
            gross_salary: Monthly gross salary in EUR
            employee_type: 'standard' or 'household' (gens de maison)
        """
        self.gross_salary = Decimal(str(gross_salary))
        self.employee_type = employee_type.lower()

        if self.employee_type not in ['standard', 'household']:
            raise ValueError("employee_type must be 'standard' or 'household'")

        # Select appropriate rate tables
        if self.employee_type == 'standard':
            self.employee_rates = self.STANDARD_EMPLOYEE_RATES
            self.employer_rates = self.STANDARD_EMPLOYER_RATES
        else:
            self.employee_rates = self.HOUSEHOLD_EMPLOYEE_RATES
            self.employer_rates = self.HOUSEHOLD_EMPLOYER_RATES

    def _calculate_contribution(self, rate: Decimal, base_salary: Decimal,
                                ceiling: Optional[Decimal] = None) -> Decimal:
        """
        Calculate a single contribution amount.

        Args:
            rate: Percentage rate (e.g., 3.60 for 3.60%)
            base_salary: Salary to apply the rate to
            ceiling: Maximum salary for this contribution (None = no ceiling)

        Returns:
            Contribution amount
        """
        # Apply ceiling if specified
        if ceiling is not None:
            base_salary = min(base_salary, ceiling)

        # Calculate contribution: base * (rate / 100)
        contribution = base_salary * (rate / Decimal('100'))

        # Round to 2 decimal places (EUR cents)
        return contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def calculate_employee_contributions(self) -> Dict[str, Decimal]:
        """
        Calculate all employee social security contributions.

        Returns:
            Dictionary with contribution categories and amounts
        """
        contributions = {}

        for category, rate in self.employee_rates.items():
            ceiling = self.CONTRIBUTION_CEILINGS.get(category)
            contributions[category] = self._calculate_contribution(
                rate, self.gross_salary, ceiling
            )

        contributions['total'] = sum(contributions.values())
        return contributions

    def calculate_employer_contributions(self) -> Dict[str, Decimal]:
        """
        Calculate all employer social security contributions.

        Returns:
            Dictionary with contribution categories and amounts
        """
        contributions = {}

        for category, rate in self.employer_rates.items():
            ceiling = self.CONTRIBUTION_CEILINGS.get(category)
            contributions[category] = self._calculate_contribution(
                rate, self.gross_salary, ceiling
            )

        contributions['total'] = sum(contributions.values())
        return contributions

    def calculate(self) -> Dict[str, Any]:
        """
        Calculate complete payslip with all contributions.

        Returns:
            Dictionary containing all payslip information
        """
        employee_contrib = self.calculate_employee_contributions()
        employer_contrib = self.calculate_employer_contributions()

        # Calculate net salary
        net_salary = self.gross_salary - employee_contrib['total']

        # Calculate total employer cost
        total_employer_cost = self.gross_salary + employer_contrib['total']

        # Calculate total contributions
        total_contributions = employee_contrib['total'] + employer_contrib['total']

        # Calculate percentages
        employee_rate = (employee_contrib['total'] / self.gross_salary * 100) if self.gross_salary > 0 else Decimal('0')
        employer_rate = (employer_contrib['total'] / self.gross_salary * 100) if self.gross_salary > 0 else Decimal('0')

        result = {
            'gross_salary': float(self.gross_salary),
            'employee_type': self.employee_type,
            'employee_contributions': {k: float(v) for k, v in employee_contrib.items()},
            'employee_total': float(employee_contrib['total']),
            'employee_rate_percent': float(employee_rate.quantize(Decimal('0.01'))),
            'net_salary': float(net_salary),
            'employer_contributions': {k: float(v) for k, v in employer_contrib.items()},
            'employer_total': float(employer_contrib['total']),
            'employer_rate_percent': float(employer_rate.quantize(Decimal('0.01'))),
            'total_employer_cost': float(total_employer_cost),
            'total_contributions': float(total_contributions),
            'calculation_date': datetime.now().isoformat(),
        }

        return result


def format_payslip_text(result: Dict[str, Any]) -> str:
    """
    Format payslip result as readable text.

    Args:
        result: Result dictionary from calculate()

    Returns:
        Formatted text representation
    """
    lines = []
    lines.append("=" * 60)
    lines.append("BULLETIN DE SALAIRE - MONACO")
    lines.append("=" * 60)
    lines.append(f"Type d'employé: {result['employee_type'].upper()}")
    lines.append(f"Date de calcul: {result['calculation_date'][:10]}")
    lines.append("")

    # Employee section
    lines.append("-" * 60)
    lines.append("SALAIRE ET COTISATIONS SALARIALES")
    lines.append("-" * 60)
    lines.append(f"Salaire brut mensuel:           {result['gross_salary']:>12.2f} €")
    lines.append("")
    lines.append("Cotisations salariales:")

    for category, amount in result['employee_contributions'].items():
        if category != 'total':
            label = category.replace('_', ' ').title()
            lines.append(f"  - {label:<30} {amount:>12.2f} €")

    lines.append(f"  {'Total cotisations salariales':<30} {result['employee_total']:>12.2f} €")
    lines.append(f"  {'Taux effectif':<30} {result['employee_rate_percent']:>11.2f} %")
    lines.append("")
    lines.append(f"{'SALAIRE NET À PAYER:':<32} {result['net_salary']:>12.2f} €")
    lines.append("")

    # Employer section
    lines.append("-" * 60)
    lines.append("COTISATIONS PATRONALES")
    lines.append("-" * 60)

    for category, amount in result['employer_contributions'].items():
        if category != 'total':
            label = category.replace('_', ' ').title()
            lines.append(f"  - {label:<30} {amount:>12.2f} €")

    lines.append(f"  {'Total cotisations patronales':<30} {result['employer_total']:>12.2f} €")
    lines.append(f"  {'Taux effectif':<30} {result['employer_rate_percent']:>11.2f} %")
    lines.append("")
    lines.append(f"{'COÛT TOTAL EMPLOYEUR:':<32} {result['total_employer_cost']:>12.2f} €")
    lines.append("")

    # Summary
    lines.append("-" * 60)
    lines.append("RÉSUMÉ")
    lines.append("-" * 60)
    lines.append(f"Salaire brut:                   {result['gross_salary']:>12.2f} €")
    lines.append(f"Cotisations totales:            {result['total_contributions']:>12.2f} €")
    lines.append(f"  - Part salariale:             {result['employee_total']:>12.2f} €")
    lines.append(f"  - Part patronale:             {result['employer_total']:>12.2f} €")
    lines.append(f"Salaire net:                    {result['net_salary']:>12.2f} €")
    lines.append(f"Coût total employeur:           {result['total_employer_cost']:>12.2f} €")
    lines.append("=" * 60)
    lines.append("")
    lines.append("IMPORTANT: Les taux utilisés sont des valeurs de référence.")
    lines.append("Vérifiez avec les taux officiels sur www.caisses-sociales.mc")
    lines.append("")

    return "\n".join(lines)


def main():
    """Command-line interface for the payslip calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate Monaco payslips with social security contributions'
    )
    parser.add_argument(
        '--gross-salary',
        type=float,
        required=True,
        help='Monthly gross salary in EUR'
    )
    parser.add_argument(
        '--employee-type',
        choices=['standard', 'household'],
        default='standard',
        help='Type of employee: standard or household (gens de maison)'
    )
    parser.add_argument(
        '--output-format',
        choices=['text', 'json'],
        default='text',
        help='Output format: text or json'
    )

    args = parser.parse_args()

    # Create calculator and compute
    calculator = MonacoPayslipCalculator(
        gross_salary=args.gross_salary,
        employee_type=args.employee_type
    )

    result = calculator.calculate()

    # Output results
    if args.output_format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_payslip_text(result))


if __name__ == '__main__':
    main()
