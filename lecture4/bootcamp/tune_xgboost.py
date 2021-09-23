"""
Example using Optuna to tune xgboost.

Optuna example that optimizes a classifier configuration for cancer dataset
using XGBoost.

In this example, we optimize the validation accuracy of cancer detection
using XGBoost. We optimize both the choice of booster model and its
hyperparameters.

"""

import dataclasses

import matplotlib.pyplot as plt
import numpy as np
import hydra

import optuna
import optuna.visualization.matplotlib

import sklearn.datasets
import sklearn.metrics
from sklearn.model_selection import train_test_split
import xgboost as xgb


def objective(trial):
    (data, target) = sklearn.datasets.load_breast_cancer(return_X_y=True)
    train_x, valid_x, train_y, valid_y = train_test_split(data, target, test_size=0.25)
    dtrain = xgb.DMatrix(train_x, label=train_y)
    dvalid = xgb.DMatrix(valid_x, label=valid_y)

    param = {
        "verbosity": 0,
        "objective": "binary:logistic",
        # use exact for small dataset.
        "tree_method": "exact",
        # defines booster, gblinear for linear functions.
        "booster": "dart",
        # L2 regularization weight.
        "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
        # L1 regularization weight.
        "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
        # sampling ratio for training data.
        "subsample": trial.suggest_float("subsample", 0.2, 1.0),
        # sampling according to each tree.
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.2, 1.0),
    }

    # maximum depth of the tree, signifies complexity of the tree.
    param["max_depth"] = trial.suggest_int("max_depth", 3, 9, step=2)
    # minimum child weight, larger the term more conservative the tree.
    param["min_child_weight"] = trial.suggest_int("min_child_weight", 2, 10)
    param["eta"] = trial.suggest_float("eta", 1e-8, 1.0, log=True)
    # defines how selective algorithm is.
    param["gamma"] = trial.suggest_float("gamma", 1e-8, 1.0, log=True)
    param["grow_policy"] = trial.suggest_categorical("grow_policy", ["depthwise", "lossguide"])

    param["sample_type"] = trial.suggest_categorical("sample_type", ["uniform", "weighted"])
    param["normalize_type"] = trial.suggest_categorical("normalize_type", ["tree", "forest"])
    param["rate_drop"] = trial.suggest_float("rate_drop", 1e-8, 1.0, log=True)
    param["skip_drop"] = trial.suggest_float("skip_drop", 1e-8, 1.0, log=True)

    bst = xgb.train(param, dtrain)
    preds = bst.predict(dvalid)
    pred_labels = np.rint(preds)
    accuracy = sklearn.metrics.accuracy_score(valid_y, pred_labels)
    return accuracy


@dataclasses.dataclass
class Config:
    n_trials: int = 100


@hydra.main(config_path=None, config_name='config')
def main(config: Config):
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=config.n_trials, timeout=600)

    print("Number of finished trials: ", len(study.trials))
    print("Best trial:")
    trial = study.best_trial

    print("  Value: {}".format(trial.value))
    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    plot_results(study)


def _savefig_axes(ax, name):
    if isinstance(ax, np.ndarray):
        ax = ax[0, 0]

    fig = ax.get_figure()
    fig.set_size_inches(16, 12)
    fig.savefig(name)
    plt.close(fig)


def plot_results(study):
    _savefig_axes(
        optuna.visualization.matplotlib.plot_optimization_history(study),
        'optimization_history.png')

    _savefig_axes(
        optuna.visualization.matplotlib.plot_param_importances(study),
        'param_importance.png')

    _savefig_axes(
        optuna.visualization.matplotlib.plot_contour(study, params=['subsample', 'colsample_bytree']),
        'contour.png')



if __name__ == "__main__":
    from hydra.core.config_store import ConfigStore
    cs = ConfigStore()
    cs.store('config', node=Config)
    main()

