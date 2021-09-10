"""This module encapsulates the places365 dataset as provided by torchvision
as a pytorch-lightning datamodule.
"""

from typing import Optional

import pytorch_lightning

import torch
import torch.utils.data
import torchvision
import torchvision.transforms


class PlacesDataModule(pytorch_lightning.LightningDataModule):
    def __init__(self, batch_size: int, root='/places365', num_data_workers: int=4):
        super().__init__()

        self.batch_size = batch_size
        self.root = root
        self.train_ds = None
        self.val_ds = None
        self.num_data_workers = num_data_workers


    def setup(self, stage: Optional[str]=None) -> None:
        # Values taken from ImageNet
        normalize = torchvision.transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])

        self.train_ds = torchvision.datasets.Places365(
            self.root, small=True,
            transform=torchvision.transforms.Compose([
                torchvision.transforms.RandomCrop(224),
                torchvision.transforms.RandomHorizontalFlip(),
                torchvision.transforms.ToTensor(),
                normalize
            ]))

        self.val_ds = torchvision.datasets.Places365(
            self.root, split='val', small=True,
            transform=torchvision.transforms.Compose([
                torchvision.transforms.CenterCrop(224),
                torchvision.transforms.ToTensor(),
                normalize
            ]))


    def train_dataloader(self):
        return torch.utils.data.DataLoader(
            self.train_ds,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_data_workers,
            persistent_workers=True)

    def val_dataloader(self):
        return torch.utils.data.DataLoader(
            self.val_ds,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_data_workers)
