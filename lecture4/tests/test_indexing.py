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
