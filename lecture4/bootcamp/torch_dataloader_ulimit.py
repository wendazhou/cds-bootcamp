"""This script creates a somewhat pathological case when using pytorch dataloaders
demonstrating potential issues that may arise when the file limit is set too low.

"""

import tqdm
import torch
import torch.utils.data


class RandomDataset(torch.utils.data.Dataset):
    def __init__(self, size: int=1000):
        self.size = size

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return torch.unbind(torch.randn(100, 10))


def create_dataloader(num_workers: int):
    dataset = RandomDataset()

    return torch.utils.data.DataLoader(
        dataset,
        num_workers=num_workers)


def main():
    dataloader = create_dataloader(num_workers=16)

    total = 0

    for _ in tqdm.trange(50):
        for ts in dataloader:
            total += torch.stack(ts).sum()

    print(f'Total value this time was: {total}')


if __name__ == '__main__':
    main()
