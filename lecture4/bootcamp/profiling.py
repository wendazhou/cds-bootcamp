"""Profiling script.

This script has functionality to benchmark matrix multiplication on the given devices.
It also demonstrates a potential pitfall of benchmarking if synchronization is not performed.

"""

import dataclasses
import time

import hydra
import torch


@dataclasses.dataclass
class BenchmarkConfig:
    """Configuration for benchmarking.

    Attributes
    ----------
    size : int
        Size of the matrix to multiply.
    repetitions : int
        Number of times to perform the matrix multiplication.
    device : str
        Device to use
    dtype : str
        Data-type to use (float16, float32 or float64)
    synchronize : bool
        If `False`, synchronization is omitted.
        Note: this leads to incorrect results!
    """
    size: int = 4096
    repetitions: int = 500
    device: str = 'cuda'
    dtype: str = 'float32'
    synchronize: bool = True


def self_multiply_matrix(m, repetitions: int):
    """This function is a busy-loop matrix multiplication.
    """
    for _ in range(repetitions):
        m = torch.matmul(m, m)
    return m


TORCH_DTYPES = {
    'float16': torch.float16,
    'float32': torch.float32,
    'float64': torch.float64
}


def benchmark(config: BenchmarkConfig):
    dtype = TORCH_DTYPES[config.dtype]
    m = torch.zeros((config.size, config.size), dtype=dtype, device=config.device)

    start_time = time.perf_counter()
    m = self_multiply_matrix(m, config.repetitions)

    if config.synchronize:
        # Get the item back to CPU, forcing synchronization
        m[0,0].item()

    end_time = time.perf_counter()

    return end_time - start_time


@hydra.main(config_path=None, config_name='config')
def main(config: BenchmarkConfig):
    total_time = benchmark(config)
    total_flops = 2 * (config.size ** 3) * config.repetitions

    print(f'Done in {total_time:.1f}s. Estimated performance {total_flops/total_time/1e12:.2f} Tflops.')


if __name__ == '__main__':
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store('config', node=BenchmarkConfig)
    main()
