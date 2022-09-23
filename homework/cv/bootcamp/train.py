import hydra
import pytorch_lightning
import pytorch_lightning.callbacks

from . import model, dataset


@hydra.main(config_name='conf', config_path=None)
def main(config: model.PlacesTrainingConfig):
    callbacks = [
        pytorch_lightning.callbacks.DeviceStatsMonitor(),
        pytorch_lightning.callbacks.LearningRateMonitor(log_momentum=True),
    ]

    trainer_kwargs = { **config.lightning }

    if config.optim.grad_clip_norm is not None:
        trainer_kwargs['gradient_clip_val'] = config.optim.grad_clip_norm

    if config.gpus > 0:
        trainer_kwargs['accelerator'] = 'gpu'
        trainer_kwargs['devices'] = config.gpus
    else:
        trainer_kwargs['accelerator'] = 'cpu'

    trainer_kwargs['callbacks'] = callbacks
    trainer_kwargs['max_epochs'] = config.max_epochs
    trainer_kwargs['precision'] = config.precision

    trainer = pytorch_lightning.Trainer(**trainer_kwargs)

    dm = dataset.PlacesDataModule(
        config.batch_size // max(config.gpus, 1),
        config.data.root,
        config.data.num_workers)

    dm.setup()

    config.data.dataset_size = len(dm.train_ds)

    mymodel = model.PlacesModel(config)

    trainer.fit(mymodel, datamodule=dm)


if __name__ == '__main__':
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store('conf', node=model.PlacesTrainingConfig)
    main()
