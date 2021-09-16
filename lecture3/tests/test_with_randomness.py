import pytest
import torch


def test_sum_random():
    # By using a generator, the random values are always the same
    gen = torch.random.manual_seed(123)
    x = torch.randn(10, generator=gen)

    assert x.sum() == pytest.approx(-3.100832)
