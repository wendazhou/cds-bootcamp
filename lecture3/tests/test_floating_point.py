import numpy as np
import pytest


def test_floating_point_associativity():
    eps = np.finfo('double').eps

    x = (eps + 1) + (1 + eps)
    y = eps + (1 + 1) + eps

    assert x != y
    assert x == pytest.approx(y)
