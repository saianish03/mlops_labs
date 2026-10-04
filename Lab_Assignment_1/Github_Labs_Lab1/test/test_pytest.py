import pytest
from src import interest


@pytest.mark.parametrize("p, r, t, expected", [
    (1000, 5, 2, 100),
    (1000, 0, 5, 0),
    (0, 10, 10, 0),
    (2000, 7.5, 4, 600),
])
def test_simple_interest(p, r, t, expected):
    assert interest.simple_interest(p, r, t) == pytest.approx(expected)


@pytest.mark.parametrize("p, r, t, n, expected", [
    (1000, 10, 2, 1, 210),
    (1000, 12, 1, 12, 126.8250301),
    (1000, 0, 5, 1, 0),
])
def test_compound_interest(p, r, t, n, expected):
    assert interest.compound_interest(p, r, t, n) == pytest.approx(expected)


def test_future_value():
    assert interest.future_value(1000, 10, 2) == pytest.approx(1210)
    assert interest.future_value(500, 0, 3) == pytest.approx(500)


@pytest.mark.parametrize("p, rate, months, expected", [
    (100000, 12, 12, 8884.8788),
    (1200, 0, 12, 100),
])
def test_monthly_emi(p, rate, months, expected):
    assert interest.monthly_emi(p, rate, months) == pytest.approx(expected, rel=1e-4)


def test_years_to_double():
    assert interest.years_to_double(8) == 9
    assert interest.years_to_double(6) == 12


@pytest.mark.parametrize("func, args", [
    (interest.simple_interest, (-1, 5, 2)),
    (interest.simple_interest, ("1000", 5, 2)),
    (interest.simple_interest, (True, 5, 2)),
    (interest.compound_interest, (1000, -5, 2)),
    (interest.future_value, (1000, 5, 2, 0)),
    (interest.future_value, (1000, 5, 2, 1.5)),
    (interest.monthly_emi, (1000, 5, 0)),
    (interest.years_to_double, (0,)),
    (interest.years_to_double, (-3,)),
])
def test_bad_input_raises(func, args):
    with pytest.raises(ValueError):
        func(*args)
