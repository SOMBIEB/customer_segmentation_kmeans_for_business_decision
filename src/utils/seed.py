import random
import numpy as np

def set_seed(seed: int = 42) -> None:
    """
    Fixe les seeds pour la reproductibilité.
    """
    random.seed(seed)
    np.random.seed(seed)
