import numpy as np
import pytest

import meow as mw


class FakeMedium:
    """Used to model a medim with off-diagonal permittivity tensor elements.
    Since tidy3d does not yet support this, this is a "fake" class that has
    an eps_comp that can behave as such, letting you give it off-diagonal
    entries.
    """
    def __init__(self, permittivity: np.ndarray, frequency: float) -> None:
        self.permittivity = permittivity
        self.frequency = frequency

    def eps_comp(self, i: int, j: int, freq: float) -> complex:
        assert freq == self.frequency
        return self.permittivity[i, j]


def test_ensure_no_off_diagonal_accepts_diagonal_tensor():
    material = mw.TidyMaterial(name="LiNbO3", variant="Zelmon1997", optical_axis="z")
    frequency = 2e14
    medium = FakeMedium(np.diag([4.0, 5.0, 6.0]), frequency)

    material._ensure_no_off_diagonal(medium, frequency)


@pytest.mark.parametrize("i, j", [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])
@pytest.mark.parametrize("value", [0.1, -0.1, 0.1j])
def test_ensure_no_off_diagonal_rejects_off_diagonal_tensor(i, j, value):
    material = mw.TidyMaterial(name="LiNbO3", variant="Zelmon1997", optical_axis="z")
    frequency = 2e14
    permittivity = np.diag([4.0, 5.0, 6.0]).astype(complex)
    permittivity[i, j] = value
    medium = FakeMedium(permittivity, frequency)

    with pytest.raises(ValueError, match="has off-diagonal permittivity components"):
        material._ensure_no_off_diagonal(medium, frequency)
