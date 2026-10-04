"""Interest calculator: simple interest, compound interest, EMI and more."""


def _validate_positive(**values):
    """Raise ValueError if any value is not a non-negative number (bools not allowed)."""
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number.")
        if value < 0:
            raise ValueError(f"{name} must not be negative.")


def simple_interest(principal, rate, years):
    """
    Simple interest earned.
    Args:
        principal (int/float): Starting amount.
        rate (int/float): Yearly interest rate in percent.
        years (int/float): Number of years.
    Returns:
        float: principal * rate * years / 100
    """
    _validate_positive(principal=principal, rate=rate, years=years)
    return principal * rate * years / 100


def compound_interest(principal, rate, years, n=1):
    """
    Compound interest earned (not the total amount).
    Args:
        principal (int/float): Starting amount.
        rate (int/float): Yearly interest rate in percent.
        years (int/float): Number of years.
        n (int): Times interest is compounded per year (1 = yearly, 12 = monthly).
    Returns:
        float: Interest earned.
    """
    return future_value(principal, rate, years, n) - principal


def future_value(principal, rate, years, n=1):
    """
    Total amount after compounding: principal + compound interest.
    Raises:
        ValueError: If inputs are invalid or n is not a positive integer.
    """
    _validate_positive(principal=principal, rate=rate, years=years)
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer.")
    return principal * (1 + rate / 100 / n) ** (n * years)


def monthly_emi(principal, annual_rate, months):
    """
    Monthly loan payment (EMI).
    Args:
        principal (int/float): Loan amount.
        annual_rate (int/float): Yearly interest rate in percent.
        months (int): Loan length in months, must be > 0.
    Returns:
        float: Monthly payment. With 0% rate, it is principal / months.
    """
    _validate_positive(principal=principal, annual_rate=annual_rate, months=months)
    if months == 0:
        raise ValueError("months must be greater than 0.")
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def years_to_double(rate):
    """
    Rule of 72: rough years for money to double at a yearly rate (percent).
    Raises:
        ValueError: If rate is not a number greater than 0.
    """
    _validate_positive(rate=rate)
    if rate == 0:
        raise ValueError("rate must be greater than 0.")
    return 72 / rate
