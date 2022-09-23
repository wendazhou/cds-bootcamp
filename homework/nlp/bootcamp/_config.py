import dataclasses

@dataclasses.dataclass
class BertFineTuningConfig:
    precision: int = 32
    max_epochs: int = 20
    batch_size: int = 8
    gpus: int = 1
