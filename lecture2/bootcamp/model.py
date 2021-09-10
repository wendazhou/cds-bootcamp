"""This module encapsulates the MobilenetV3 model provided by the torchvision package
as a pytorch lightning module.

"""

import dataclasses
from typing import Any, Dict, Optional

import omegaconf
import pytorch_lightning
import torchvision
import torch
import torchmetrics


@dataclasses.dataclass
class PlacesModelConfig:
    width_multiplier: float = 1.0


@dataclasses.dataclass
class PlacesOptimConfig:
    learning_rate: float = 1e-2
    weight_decay: float = 1e-5
    grad_clip_norm: Optional[float] = None


@dataclasses.dataclass
class PlacesDataConfig:
    root: str = '/places365'
    dataset_size: Optional[int] = None
    num_workers: int = 4


@dataclasses.dataclass
class PlacesTrainingConfig:
    data: PlacesDataConfig = PlacesDataConfig()
    model: PlacesModelConfig = PlacesModelConfig()
    optim: PlacesOptimConfig = PlacesOptimConfig()
    lightning: Dict[str, Any] = dataclasses.field(default_factory=dict)
    batch_size: int = 256
    max_epochs: int = 60
    gpus: int = 1


class PlacesModel(pytorch_lightning.LightningModule):
    hparams: PlacesTrainingConfig

    def __init__(self, config: PlacesTrainingConfig):
        super().__init__()

        if not isinstance(config, omegaconf.DictConfig):
            config = omegaconf.OmegaConf.structured(config)

        self.save_hyperparameters(config)
        self.model = torchvision.models.mobilenet.mobilenet_v3_large(num_classes=365, _width_mult=config.model.width_multiplier)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.accuracy_top1 = torchmetrics.Accuracy(num_classes=365)
        self.accuracy_top5 = torchmetrics.Accuracy(num_classes=365, top_k=5)

    def forward(self, img):
        return self.model(img)

    def _compute_loss(self, batch):
        img, label = batch
        logits = self(img)

        loss = self.criterion(logits, label)
        acc_top1 = self.accuracy_top1(logits, label)
        acc_top5 = self.accuracy_top5(logits, label)

        return loss, {'accuracy_top1': acc_top1, 'accuracy_top5': acc_top5}

    def training_step(self, batch, *_):
        loss, metrics = self._compute_loss(batch)

        self.log('accuracy', metrics['accuracy_top1'], prog_bar=True)

        return loss

    def validation_step(self, batch, *_):
        loss, _ = self._compute_loss(batch)

        self.log('val/loss', loss)
        self.log('val/accuracy_top1', self.accuracy_top1)
        self.log('val/accuracy_top5', self.accuracy_top5)

    def configure_optimizers(self):
        base_lr = self.hparams.optim.learning_rate / 256 * self.hparams.batch_size

        opt = torch.optim.SGD(
            self.parameters(),
            base_lr, momentum=0.9,
            weight_decay=self.hparams.optim.weight_decay)

        steps_per_epoch = (self.hparams.data.dataset_size + self.hparams.batch_size - 1) // self.hparams.batch_size

        lr_scheduler = torch.optim.lr_scheduler.OneCycleLR(
            opt,
            max_lr=base_lr * 10,
            epochs=self.hparams.max_epochs,
            steps_per_epoch=steps_per_epoch)

        scheduler_config = {
            'scheduler': lr_scheduler,
            'interval': 'step',
            'frequency': 1
        }

        return [opt], [scheduler_config]
