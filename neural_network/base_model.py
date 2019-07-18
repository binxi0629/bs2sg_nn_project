import torch.nn as nn


def get_bs2sg():
    layers = [
        nn.LeakyReLU(),
        nn.Linear(360, 100),
        nn.LeakyReLU(),
        nn.Linear(100, 100),
        nn.Linear(100, 230),
        nn.LeakyReLU(),
        nn.LeakyReLU(),
    ]
    model = nn.Sequential(*layers)
    return model


def get_bs2cs():
    layers = [
        nn.LeakyReLU(),
        nn.Linear(1200, 256),
        nn.LeakyReLU(),
        nn.Linear(256, 128),
        nn.LeakyReLU(),
        nn.Linear(128, 7)
    ]
    model = nn.Sequential(*layers)
    return model


def get_cs2sg(*args):
    layers = []
    for i in range(len(args) - 1):
        layers.append(nn.LeakyReLU())
        layers.append(nn.Linear(args[i], args[i+1]))
    model = nn.Sequential(*layers)
    return model