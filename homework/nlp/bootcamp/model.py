
from __future__ import annotations

import pytorch_lightning
import torch
import torchmetrics
import transformers

from transformers import AutoModelForSequenceClassification


class PretrainedBertModel(pytorch_lightning.LightningModule):
    def __init__(self):
        super().__init__()

        self.model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=5)
        self.accuracy = torchmetrics.Accuracy(num_classes=5)

    def forward(self, batch):
        return self.model(**batch)

    def training_step(self, batch, batch_idx):
        outputs = self.forward(batch)
        loss = outputs.loss

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        self.accuracy(predictions, batch["labels"])

        self.log("train/loss", loss)
        self.log("train/accuracy", self.accuracy)

        return loss

    def validation_step(self, batch, batch_idx):
        outputs = self.forward(batch)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        self.accuracy(predictions, batch["labels"])

        self.log("val/loss", outputs.loss)
        self.log("val/accuracy", self.accuracy)

        return outputs.loss


    def configure_optimizers(self):
        optim = torch.optim.AdamW(self.parameters(), lr=5e-5)
        lr = transformers.get_scheduler(
            name="linear",
            optimizer=optim,
            num_warmup_steps=0,
            num_training_steps=self.trainer.estimated_stepping_batches)
        return [optim], [lr]
