import pytest
import torch


# Basic parametrization
@pytest.mark.parametrize('num_elements', [10, 20])
def test_pytorch_sum(num_elements):
    x = torch.zeros(num_elements, dtype=torch.int32)
    assert x.sum() == 0


# Multiple parametrization
@pytest.mark.parametrize('num_elements,dtype', [(10, torch.int32), (20, torch.int64)])
def test_pytorch_sum_multiple(num_elements, dtype):
    x = torch.zeros(num_elements, dtype=dtype)
    assert x.sum() == 0


# Parametrization with conditional skipping
@pytest.mark.parametrize(
    'device',
    ['cpu',
     pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='Cuda required'))])
def test_pytorch_sum_device(device):
    x = torch.ones(10, device=device, dtype=torch.int32)
    assert x.sum() == 10

