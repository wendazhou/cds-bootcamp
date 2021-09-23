"""Demonstration for CIFAR-10 learning rate.

This script is intended to demonstrate a couple aspects of setting learning rates and batch size.

1. Changing training speed as a function of batch size
    Larger batch sizes lead to significantly improved performance for training.
    Change the batch size from 64 to 2048 to see the difference in training speed.

2. Batch size (not) affecting accuracy
    By correctly scaling the learning rate as a function of batch size, batch size mostly
    has little effect on the final accuracy, as long as the batch size is not too large.
    However, if the scaling is not correctly done, then there will be substantial changes
    in the performance.

    Control this demonstration by varying the batch size, and setting the argument:
    `scale_lr_by_bs` to `True` to see correct scaling, and `False` to see incorrect scaling.

3. Warmup for large batch training
    When using very large batches, we need to slowly ramp up the learning rate to achieve
    good stability.

    Note that here it does not affect results much, but see this paper:
    https://arxiv.org/pdf/1706.02677.pdf
    for more information.

"""

import dataclasses
import time
from typing import List, Iterable, Optional, Sequence, Tuple

import numpy as np

import hydra
import tqdm
import torch
import torch.nn
import torch.nn.functional
import torch.optim


@dataclasses.dataclass
class Config:
    batch_size: int = 512
    learning_rate: float = 1e-2
    scale_lr_by_bs: bool = True
    warmup_lr: bool = False
    max_epochs: int = 50
    data_folder: str = './data'

class SimpleConvNet(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = torch.nn.Conv2d(3, 6, 5)
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.conv2 = torch.nn.Conv2d(6, 16, 5)
        self.fc1 = torch.nn.Linear(16 * 5 * 5, 120)
        self.fc2 = torch.nn.Linear(120, 84)
        self.fc3 = torch.nn.Linear(84, 10)

    def forward(self, x: torch.Tensor):
        x = self.pool(torch.nn.functional.relu(self.conv1(x)))
        x = self.pool(torch.nn.functional.relu(self.conv2(x)))

        x = torch.flatten(x, start_dim=1)

        x = torch.nn.functional.relu(self.fc1(x))
        x = torch.nn.functional.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class InMemoryDataloader:
    """Utility class which exposes the data as an iterable sequence, but holds
    all of the data in (GPU) memory instead of loading it bit by bit.
    """

    def __init__(self, tensors: Sequence[torch.Tensor], batch_size: int, generator: Optional[torch.Generator]=None, subset: torch.Tensor=None):
        self.tensors = tensors
        self.batch_size = batch_size
        self.generator = generator
        self.subset = subset

    @property
    def dataset_size(self):
        if self.subset is not None:
            return len(self.subset)
        else:
            return len(self.tensors[0])

    def __len__(self):
        return (self.dataset_size + self.batch_size - 1) // self.batch_size

    def __iter__(self):
        perm = torch.randperm(self.dataset_size, generator=self.generator)
        perm.to(device=self.tensors[0].device)

        for i in range(len(self)):
            idx = perm[i * self.batch_size:(i + 1) * self.batch_size]
            if self.subset is not None:
                idx = self.subset[idx]
            yield (t[idx] for t in self.tensors)


def make_warmup_scheduler(optim, batches_per_epoch: int, num_warmup_epochs: int=5):
    num_warmup_batches = batches_per_epoch * num_warmup_epochs

    return torch.optim.lr_scheduler.LambdaLR(
        optim, lambda step: min(step / num_warmup_batches, 1))


def train_epoch(model: torch.nn.Module, optim: torch.optim.Optimizer, scaler: torch.cuda.amp.GradScaler, dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]], scheduler=None) -> List[float]:
    """Train the model for a single epoch."""
    loss_values = []

    for data in dataloader:
        inputs, labels = data

        optim.zero_grad()

        with torch.cuda.amp.autocast():
            outputs = model.forward(inputs)
            loss = torch.nn.functional.cross_entropy(outputs, labels)

        # Note: for better performance, we are using 16-bit training,
        # so we are also using loss scaling here.
        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.step(optim)
            scaler.update()
        else:
            loss.backward()
            optim.step()

        if scheduler is not None:
            # Step the scheduler.
            # Note that we are stepping per batch, not per epoch here!
            scheduler.step()

        loss_values.append(loss.detach().to(device='cpu', non_blocking=True))

    return [l.item() for l in loss_values]

def eval_model(model: torch.nn.Module, dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]]):
    with torch.no_grad():
        total_loss = 0
        total_correct = 0
        total_observations = 0

        for data in dataloader:
            inputs, labels = data

            outputs = model.forward(inputs)
            loss = torch.nn.functional.cross_entropy(outputs, labels, reduction='sum')
            predicted = torch.argmax(outputs, dim=-1)
            accuracy = torch.sum(predicted == labels)

            total_loss += loss
            total_correct += accuracy
            total_observations += inputs.shape[0]

        loss = total_loss.item() / total_observations
        accuracy = total_correct.item() / total_observations

    return loss, accuracy


def create_dataloader(batch_size, seed: int, dtype=torch.float32, device='cpu', train=True, data_folder='./data'):
    import torchvision
    data_folder = hydra.utils.to_absolute_path(data_folder)
    ds = torchvision.datasets.CIFAR10(data_folder, train=train, download=True)

    images = torch.from_numpy(ds.data).to(dtype=dtype, device=device).div_(256).sub_(0.5).div_(0.5).permute(0, 3, 1, 2)
    labels = torch.tensor(ds.targets, dtype=torch.int64, device=device)

    generator = torch.Generator().manual_seed(seed)

    return InMemoryDataloader((images, labels), batch_size, generator=generator)


def train(config: Config):
    device = torch.device('cuda')
    model = SimpleConvNet().to(device=device, memory_format=torch.channels_last)

    lr = config.learning_rate
    if config.scale_lr_by_bs:
        # reference learning rate at bs=256
        lr *= (config.batch_size / 256)

    optim = torch.optim.SGD(model.parameters(), lr=lr)
    scaler = torch.cuda.amp.GradScaler()

    dataloader = create_dataloader(config.batch_size, 0, device=device, data_folder=config.data_folder)
    test_dataloader = create_dataloader(config.batch_size, 0, device=device, train=False, data_folder=config.data_folder)

    if config.warmup_lr:
        scheduler = make_warmup_scheduler(optim, len(dataloader))
    else:
        scheduler = None


    start_time = time.perf_counter()

    for _ in tqdm.trange(50):
        epoch_loss = train_epoch(model, optim, scaler, dataloader, scheduler=scheduler)

    end_time = time.perf_counter()

    final_loss, final_accuracy = eval_model(model, test_dataloader)
    print(f'Final train loss: {np.mean(epoch_loss)}')
    print(f'Final loss {final_loss:.3f}, final accuracy {final_accuracy:.2%}.')
    print(f'Total time: {end_time - start_time:.1f} s.')


@hydra.main(config_name='config', config_path=None)
def main(config: Config):
    train(config)

if __name__ == '__main__':
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store(name='config', node=Config)
    main()
