import numpy as np


def constant_function(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2


# with type annotations, we get better IDE functionality (e.g. autocomplete)
def constant_function_typed(x: np.ndarray) -> np.ndarray:
    return constant_function(x)


def incorrect_mean(x):
    # this function is intentionally incorrectly implemented
    return np.sum(x)

