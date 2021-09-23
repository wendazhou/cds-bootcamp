"""Example failing tests and debugging CUDA

These tests below fail because the label is out of bound for the current model.
The model expects to classify CIFAR-10, which has 10 labels, which would be labelled
from 0 to 9. However, I have created a fake label 10, and passed that in to the model.
This will introduce an error when computing the loss.

"""

import torch

from bootcamp import train_lr


def test_simple_convnet_integration():
    device = 'cuda'

    labels = torch.tensor([0, 10, 5, 2]).to(device)
    images = torch.randn([4, 3, 32, 32]).to(device, memory_format=torch.channels_last)

    model = train_lr.SimpleConvNet().to(device=device, memory_format=torch.channels_last)
    optim = torch.optim.SGD(model.parameters(), lr=1e-2)

    scaler = torch.cuda.amp.GradScaler()
    dataloader = train_lr.InMemoryDataloader((images, labels), batch_size=2)

    result = train_lr.train_epoch(model, optim, scaler, dataloader)
    assert len(result) == 2


def test_simple_convnet_integration_cpu():
    device = 'cpu'

    labels = torch.tensor([0, 10, 5, 2]).to(device)
    images = torch.randn([4, 3, 32, 32]).to(device, memory_format=torch.channels_last)

    model = train_lr.SimpleConvNet().to(device=device, memory_format=torch.channels_last)
    optim = torch.optim.SGD(model.parameters(), lr=1e-2)

    scaler = None # Scaler not enable on CPU
    dataloader = train_lr.InMemoryDataloader((images, labels), batch_size=2)

    result = train_lr.train_epoch(model, optim, scaler, dataloader)
    assert len(result) == 2
