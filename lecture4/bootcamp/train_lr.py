"""Demonstration for CIFAR-10 learning rate.
"""

from typing import List, Iterable, Optional, Sequence, Tuple

import torch
import torch.nn
import torch.nn.functional
import torch.optim

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
    def __init__(self, tensors: Sequence[torch.Tensor], batch_size: int, generator: Optional[torch.Generator]=None):
        self.tensors = tensors
        self.batch_size = batch_size
        self.generator = generator

    @property
    def dataset_size(self):
        return len(self.tensors[0])

    def __len__(self):
        return (self.dataset_size + self.batch_size - 1) // self.batch_size

    def __iter__(self):
        perm = torch.randperm(self.dataset_size, generator=self.generator)

        for i in range(len(self)):
            idx = perm[i * self.batch_size:(i + 1) * self.batch_size]
            return (t[idx] for t in self.tensors)


def train_epoch(model: torch.nn.Module, optim: torch.optim.Optimizer, dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]]) -> List[float]:
    loss_values = []

    for data in dataloader:
        inputs, labels = data

        optim.zero_grad()

        outputs = model.forward(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, labels)
        loss.backward()
        optim.step()

        loss_values.append(loss.detach().to(device='cpu', non_blocking=True))

    return [l.item() for l in loss_values]
