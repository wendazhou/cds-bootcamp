import os

import numpy as np
import pytest


@pytest.fixture
def data() -> np.ndarray:
    current_dir = os.path.dirname(__file__)
    return np.load(os.path.join(current_dir, 'testdata', 'sample.npy'))


def test_sum_of_data(data):
    # Here, data is automatically loaded by calling the eponymous function
    assert np.sum(data) == pytest.approx(-5.22075629)
