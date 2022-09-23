"""This module provides a convenient interface to the yelp dataset through
pytorch lightning and huggingface datasets.
"""

import functools
import os

import datasets
import pytorch_lightning
import torch
import torch.utils.data
from transformers import AutoTokenizer


def _tokenize(examples, tokenizer):
    return tokenizer(examples["text"], padding='max_length', truncation=True)

def _load_ds():
    ds = datasets.load_dataset("yelp_review_full")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased", use_fast=True)
    ds = ds.map(
        functools.partial(_tokenize, tokenizer=tokenizer),
        batched=True,
        num_proc=len(os.sched_getaffinity(0)))
    ds = ds.remove_columns(["text"])
    ds = ds.rename_column("label", "labels")
    ds.set_format("torch")
    return ds


class YelpDataModule(pytorch_lightning.LightningDataModule):
    def __init__(self, batch_size: int = 8, num_workers: int = 4):
        super().__init__()

        # We work on a small subset of the dataset to speed up processing
        ds = _load_ds()
        self.ds_train = ds["train"].shuffle(seed=42).select(range(20000))
        self.ds_test = ds["test"].shuffle(seed=42).select(range(1000))
        self.batch_size = batch_size
        self.num_workers = num_workers

    def _make_dataloader(self, ds, shuffle):
        return torch.utils.data.DataLoader(
            ds,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=True,
            persistent_workers=self.num_workers > 0)

    def train_dataloader(self):
        return self._make_dataloader(self.ds_train, True)

    def val_dataloader(self):
        return self._make_dataloader(self.ds_test, False)
