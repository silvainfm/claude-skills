#!/usr/bin/env python3
"""
Monaco Payslip Calculator
Calculates employer and employee social security contributions for Monaco payslips.

Based on official rates from Caisses Sociales de Monaco effective October 1, 2025.

Usage:
    python3 payslip_calculator.py --gross-salary 3500 --employee-type household
    python3 payslip_calculator.py --gross-salary 2500 --employee-type household --output-format json
"""

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class MonacoPayslipCalculator:
    """
    Calculator for Monaco payslips (bulletin de salaire).

    Handles calculation of social security contributions according to
    Monaco's Caisses Sociales system (rates effective October 1, 2025).
    """

    # CCSS (Caisses de Compensation pour les Services Sociaux) - Social Security
    # Rate: 13.40% of the contribution base
    # For household employees (1-2 employees, <254h/month): base = 33% of gross salary
    # Otherwise: base = full gross salary
    CCSS_RATE = Decimal('13.40')
    CCSS_HOUSEHOLD_BASE_PERCENTAGE = Decimal('33.00')  # For household employees
    CCSS_MONTHLY_CEILING = Decimal('9800.00')

    # C.A.R. (Caisse Autonome des Retraites) - Retirement/Pension
    CAR_EMPLOYEE_RATE = Decimal('6.85')
    CAR_EMPLOYER_RATE = Decimal('8.33')
    CAR_TOTAL_RATE = Decimal('15.18')
    CAR_MONTHLY_CEILING = Decimal('6112.00')

    # CMRC (Caisse Monégasque de Retraites Complémentaires) - Supplementary Pension
    # Tranche A (up to €3,971)
    CMRC_TRANCHE_A_CEILING = Decimal('3971.00')
    CMRC_TRANCHE_A_RATE_TOTAL = Decimal('10.02')  # 7.87% + 2.15%
    CMRC_TRANCHE_A_EMPLOYER_PERCENT = Decimal('60.00')  # 60% employer
    CMRC_TRANCHE_A_EMPLOYEE_PERCENT = Decimal('40.00')  # 40% employee

    # Tranche B (between Tranche A and 8x Tranche A)
    CMRC_TRANCHE_B_RATE_TOTAL = Decimal('24.29')  # 21.59% + 2.70%
    CMRC_TRANCHE_B_EMPLOYER_PERCENT = Decimal('60.00')  # 60% employer
    CMRC_TRANCHE_B_EMPLOYEE_PERCENT = Decimal('40.00')  # 40% employee
    CMRC_TRANCHE_B_MAX = CMRC_TRANCHE_A_CEILING * Decimal('8')  # 8x Tranche A ceiling

    # Rates source and effective date
    RATES_EFFECTIVE_DATE = "2025-10-01"
    RATES_SOURCE = "Caisses Sociales de Monaco"

    def __init__(self, gross_salary: float, employee_type: str = 'household',
                 monthly_hours: Optional[float] = None):
        """
        Initialize the payslip calculator.

        Args:
            gross_salary: Monthly gross salary in EUR
            employee_type: 'household' (gens de maison) or 'standard'
            monthly_hours: Monthly hours worked (for household employees)
        """
        self.gross_salary = Decimal(str(gross_salary))
        self.employee_type = employee_type.lower()
        self.monthly_hours = Decimal(str(monthly_hours)) if monthly_hours else None

        if self.employee_type not in ['household', 'standard']:
            raise ValueError("employee_type must be 'household' or 'standard'")

    def _calculate_contribution(self, rate: Decimal, base_salary: Decimal,
                                ceiling: Optional[Decimal] = None) -> Decimal:
        """
        Calculate a single contribution amount.

        Args:
            rate: Percentage rate (e.g., 13.40 for 13.40%)
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

    def _get_ccss_base(self) -> Decimal:
        """
        Calculate the CCSS contribution base.

        For household employees with 1-2 employees and <254 hours/month,
        the base is 33% of gross salary. Otherwise it's the full gross salary.

        Returns:
            CCSS contribution base
        """
        if self.employee_type == 'household':
            # For household employees, use 33% of gross salary as base
            # (This applies to employers with 1-2 household employees, <254h/month)
            base = self.gross_salary * (self.CCSS_HOUSEHOLD_BASE_PERCENTAGE / Decimal('100'))
        else:
            # For standard employees, use full gross salary
            base = self.gross_salary

        # Apply ceiling
        base = min(base, self.CCSS_MONTHLY_CEILING)
        return base

    def _calculate_cmrc_tranche(self, salary: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Calculate CMRC (supplementary pension) contributions split by tranches.

        Returns:
            Tuple of (employee_contribution, employer_contribution)
        """
        employee_total = Decimal('0')
        employer_total = Decimal('0')

        # Tranche A: up to €3,971
        tranche_a_base = min(salary, self.CMRC_TRANCHE_A_CEILING)
        if tranche_a_base > 0:
            tranche_a_total = self._calculate_contribution(
                self.CMRC_TRANCHE_A_RATE_TOTAL, tranche_a_base
            )
            employer_total += tranche_a_total * (self.CMRC_TRANCHE_A_EMPLOYER_PERCENT / Decimal('100'))
            employee_total += tranche_a_total * (self.CMRC_TRANCHE_A_EMPLOYEE_PERCENT / Decimal('100'))

        # Tranche B: from €3,971 to 8x €3,971 (€31,768)
        if salary > self.CMRC_TRANCHE_A_CEILING:
            tranche_b_base = min(
                salary - self.CMRC_TRANCHE_A_CEILING,
                self.CMRC_TRANCHE_B_MAX - self.CMRC_TRANCHE_A_CEILING
            )
            if tranche_b_base > 0:
                tranche_b_total = self._calculate_contribution(
                    self.CMRC_TRANCHE_B_RATE_TOTAL, tranche_b_base
                )
                employer_total += tranche_b_total * (self.CMRC_TRANCHE_B_EMPLOYER_PERCENT / Decimal('100'))
                employee_total += tranche_b_total * (self.CMRC_TRANCHE_B_EMPLOYEE_PERCENT / Decimal('100'))

        # Round final amounts
        employee_total = employee_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        employer_total = employer_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return employee_total, employer_total

    def calculate_employee_contributions(self) -> Dict[str, Decimal]:
        """
        Calculate all employee social security contributions.

        Returns:
            Dictionary with contribution categories and amounts
        """
        contributions = {}

        # C.A.R. (Retirement) - Employee portion
        car_base = min(self.gross_salary, self.CAR_MONTHLY_CEILING)
        contributions['car_retirement'] = self._calculate_contribution(
            self.CAR_EMPLOYEE_RATE, car_base
        )

        # CMRC (Supplementary Pension) - Employee portion
        cmrc_employee, _ = self._calculate_cmrc_tranche(self.gross_salary)
        contributions['cmrc_supplementary_pension'] = cmrc_employee

        contributions['total'] = sum(contributions.values())
        return contributions

    def calculate_employer_contributions(self) -> Dict[str, Decimal]:
        """
        Calculate all employer social security contributions.

        Returns:
            Dictionary with contribution categories and amounts
        """
        contributions = {}

        # CCSS (Social Security) - Employer pays all
        ccss_base = self._get_ccss_base()
        contributions['ccss_social_security'] = self._calculate_contribution(
            self.CCSS_RATE, ccss_base
        )

        # C.A.R. (Retirement) - Employer portion
        car_base = min(self.gross_salary, self.CAR_MONTHLY_CEILING)
        contributions['car_retirement'] = self._calculate_contribution(
            self.CAR_EMPLOYER_RATE, car_base
        )

        # CMRC (Supplementary Pension) - Employer portion
        _, cmrc_employer = self._calculate_cmrc_tranche(self.gross_salary)
        contributions['cmrc_supplementary_pension'] = cmrc_employer

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
            'rates_effective_date': self.RATES_EFFECTIVE_DATE,
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
            'ccss_base_used': float(self._get_ccss_base()),
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
    lines.append("=" * 70)
    lines.append("BULLETIN DE SALAIRE - PRINCIPAUTÉ DE MONACO")
    lines.append("=" * 70)
    lines.append(f"Type d'employé: {result['employee_type'].upper()}")
    lines.append(f"Date de calcul: {result['calculation_date'][:10]}")
    lines.append(f"Taux en vigueur au: {result['rates_effective_date']}")
    lines.append("")

    # Employee section
    lines.append("-" * 70)
    lines.append("SALAIRE ET COTISATIONS SALARIALES")
    lines.append("-" * 70)
    lines.append(f"Salaire brut mensuel:              {result['gross_salary']:>15.2f} €")
    lines.append("")
    lines.append("Cotisations salariales:")

    contrib_labels = {
        'car_retirement': 'C.A.R. - Retraite (6,85%)',
        'cmrc_supplementary_pension': 'CMRC - Retraite complémentaire',
    }

    for category, amount in result['employee_contributions'].items():
        if category != 'total':
            label = contrib_labels.get(category, category.replace('_', ' ').title())
            lines.append(f"  - {label:<38} {amount:>15.2f} €")

    lines.append(f"  {'Total cotisations salariales':<38} {result['employee_total']:>15.2f} €")
    lines.append(f"  {'Taux effectif':<38} {result['employee_rate_percent']:>14.2f} %")
    lines.append("")
    lines.append(f"{'SALAIRE NET À PAYER:':<40} {result['net_salary']:>15.2f} €")
    lines.append("")

    # Employer section
    lines.append("-" * 70)
    lines.append("COTISATIONS PATRONALES")
    lines.append("-" * 70)

    employer_labels = {
        'ccss_social_security': f'CCSS - Sécurité sociale (13,40%) *',
        'car_retirement': 'C.A.R. - Retraite (8,33%)',
        'cmrc_supplementary_pension': 'CMRC - Retraite complémentaire',
    }

    for category, amount in result['employer_contributions'].items():
        if category != 'total':
            label = employer_labels.get(category, category.replace('_', ' ').title())
            lines.append(f"  - {label:<38} {amount:>15.2f} €")

    lines.append(f"  {'Total cotisations patronales':<38} {result['employer_total']:>15.2f} €")
    lines.append(f"  {'Taux effectif':<38} {result['employer_rate_percent']:>14.2f} %")
    lines.append("")
    lines.append(f"{'COÛT TOTAL EMPLOYEUR:':<40} {result['total_employer_cost']:>15.2f} €")
    lines.append("")

    # Summary
    lines.append("-" * 70)
    lines.append("RÉSUMÉ")
    lines.append("-" * 70)
    lines.append(f"Salaire brut:                      {result['gross_salary']:>15.2f} €")
    lines.append(f"Cotisations totales:               {result['total_contributions']:>15.2f} €")
    lines.append(f"  - Part salariale:                {result['employee_total']:>15.2f} €")
    lines.append(f"  - Part patronale:                {result['employer_total']:>15.2f} €")
    lines.append(f"Salaire net:                       {result['net_salary']:>15.2f} €")
    lines.append(f"Coût total employeur:              {result['total_employer_cost']:>15.2f} €")
    lines.append("=" * 70)
    lines.append("")

    # Add note about CCSS base for household employees
    if result['employee_type'] == 'household':
        lines.append("* CCSS: Pour les employés de maison (1-2 employés, <254h/mois),")
        lines.append(f"  la base de cotisation = 33% du salaire brut = {result['ccss_base_used']:.2f} €")
        lines.append("")

    lines.append("Taux officiels en vigueur au 1er octobre 2025")
    lines.append("Source: Caisses Sociales de Monaco - www.caisses-sociales.mc")
    lines.append("")

    return "\n".join(lines)


def main():
    """Command-line interface for the payslip calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate Monaco payslips with social security contributions (rates effective Oct 1, 2025)'
    )
    parser.add_argument(
        '--gross-salary',
        type=float,
        required=True,
        help='Monthly gross salary in EUR'
    )
    parser.add_argument(
        '--employee-type',
        choices=['household', 'standard'],
        default='household',
        help='Type of employee: household (gens de maison) or standard'
    )
    parser.add_argument(
        '--monthly-hours',
        type=float,
        help='Monthly hours worked (for household employees)'
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
        employee_type=args.employee_type,
        monthly_hours=args.monthly_hours
    )

    result = calculator.calculate()

    # Output results
    if args.output_format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_payslip_text(result))


if __name__ == '__main__':
    main()
