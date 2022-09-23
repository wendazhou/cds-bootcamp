import hydra
import pytorch_lightning
import pytorch_lightning.callbacks

from . import dataset, model

from ._config import BertFineTuningConfig

@hydra.main(config_name='conf', config_path=None)
def main(config: BertFineTuningConfig):
    callbacks = [
        pytorch_lightning.callbacks.DeviceStatsMonitor(),
        pytorch_lightning.callbacks.LearningRateMonitor(log_momentum=True),
    ]

    trainer_kwargs = {}

    if config.gpus > 0:
        trainer_kwargs['accelerator'] = 'gpu'
        trainer_kwargs['devices'] = config.gpus
    else:
        trainer_kwargs['accelerator'] = 'cpu'

    trainer_kwargs['callbacks'] = callbacks
    trainer_kwargs['max_epochs'] = config.max_epochs
    trainer_kwargs['precision'] = config.precision

    trainer = pytorch_lightning.Trainer(**trainer_kwargs)

    dm = dataset.YelpDataModule(
        batch_size=config.batch_size // max(config.gpus, 1),
        num_workers=4)
    dm.setup()

    mymodel = model.PretrainedBertModel()
    trainer.fit(mymodel, datamodule=dm)


if __name__ == '__main__':
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store('conf', node=BertFineTuningConfig)
    main()