from bootcamp_example import myfunctions

import pytest
import numpy as np


def test_constant_function_is_one():
    # Use pytest.approx, or numpy.allclose when testing for floating point equality
    assert myfunctions.constant_function(123) == pytest.approx(1)


def test_constant_function_typed_is_one():
    assert myfunctions.constant_function_typed(np.random.randn(10)).sum() == pytest.approx(10)


def test_mean_function_is_correct():
    # Intentionally failing test for demonstration purposes
    assert myfunctions.incorrect_mean([0, 2]) == pytest.approx(1)
