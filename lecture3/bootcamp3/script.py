import dataclasses
import os
from typing import List

import hydra


@dataclasses.dataclass
class ModelConfig:
    """Configuration for the model.

    Note that `block_sizes` must be specified using the `dataclasses.field`
    function, as you are not allowed to supply default values for mutable fields.
    Instead, the default value is supplied through a default factory function which
    creates a new list every time.
    """
    architecture: str = 'lenet'
    hidden_size: int = 20
    block_sizes: List[int] = dataclasses.field(default_factory=lambda: [10, 10, 10])


@dataclasses.dataclass
class TrainingConfig:
    model: ModelConfig = ModelConfig()
    num_epochs: int = 10
    data_path: str = 'data.npy'


@hydra.main(config_path=None, config_name='config')
def main(config: TrainingConfig):
    print(f'Got configuration: {config}')

    # Note here: when loading data, should convert to absolute path
    data_path = hydra.utils.to_absolute_path(config.data_path)
    print(f'Loading data from {data_path}')

    # Note here: saving to relative path is set to output folder
    result_path = os.path.abspath('result.txt')
    print(f'Saving results to {result_path}')


if __name__ == '__main__':
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store('config', node=TrainingConfig)
    main()
