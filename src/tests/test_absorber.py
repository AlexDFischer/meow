import numpy as np
import pytest
from pydantic import ValidationError

import meow as mw
from meow import AbsorberParams


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("end_extinction_coef", -0.1),
        ("end_extinction_coef", np.inf),
        ("end_extinction_coef", np.nan),
        ("transition_power", -1),
        ("transition_power", 0),
        ("transition_power", np.inf),
        ("transition_power", np.nan),
    ],
)
def test_absorber_rejects_invalid_profile(field: str, value: float) -> None:
    with pytest.raises(ValidationError, match=field):
        AbsorberParams(length=1, **{field: value})


def test_absorber_extinction():
    absorber = AbsorberParams(length=3, end_extinction_coef=0.2, transition_power=2)
    distance = np.linspace(0, 3, 100).reshape((100, 1))
    extinction = absorber.extinction_coef(distance)
    assert extinction.shape == distance.shape
    assert np.allclose(extinction, 0.2 * ((3 - distance) / 3) ** 2)


def test_absorber_resolution_after_mesh_copy() -> None:
    # Test that model_copy copies private fields, which it didn't do under a previous
    # way I had set them up
    mesh = mw.Mesh2D(x=np.arange(5), y=np.arange(5))
    absorber = AbsorberParams(length=1)
    with_absorber = mesh.model_copy(update={"absorbing_boundary_right": absorber})
    without_absorber = with_absorber.model_copy(
        update={"absorbing_boundary_right": None}
    )

    assert mesh._absorber_right is None
    assert with_absorber._absorber_right is absorber
    assert without_absorber._absorber_right is None


def test_absorber_resolution():
    # Test that passing various combinations of
    # absorbing_boundary<, _x, _y, _left, _right, _top, _bottom> correctly resolves to
    # the internal _absorber_<left,right,top,bottom> attributes
    # and raises ValueError for illegal combinations.

    absorber1 = AbsorberParams(length=3, end_extinction_coef=0.2, transition_power=2)
    absorber2 = AbsorberParams(length=2, end_extinction_coef=0.1, transition_power=3)

    ##### Valid combinations

    mesh = mw.Mesh2D(
        x=np.linspace(0, 10, 11),
        y=np.linspace(0, 10, 11),
        absorbing_boundary=absorber1,
    )
    assert mesh._absorber_left is absorber1
    assert mesh._absorber_right is absorber1
    assert mesh._absorber_top is absorber1
    assert mesh._absorber_bottom is absorber1

    mesh = mw.Mesh2D(
        x=np.linspace(0, 10, 11),
        y=np.linspace(0, 10, 11),
        absorbing_boundary_x=absorber2,
    )
    assert mesh._absorber_left is absorber2
    assert mesh._absorber_right is absorber2
    assert mesh._absorber_top is None
    assert mesh._absorber_bottom is None

    mesh = mw.Mesh2D(
        x=np.linspace(0, 10, 11),
        y=np.linspace(0, 10, 11),
        absorbing_boundary_y=absorber2,
    )
    assert mesh._absorber_left is None
    assert mesh._absorber_right is None
    assert mesh._absorber_top is absorber2
    assert mesh._absorber_bottom is absorber2

    mesh = mw.Mesh2D(
        x=np.linspace(0, 10, 11),
        y=np.linspace(0, 10, 11),
        absorbing_boundary_left=absorber1,
        absorbing_boundary_right=absorber2,
        absorbing_boundary_top=absorber1,
        absorbing_boundary_bottom=absorber2,
    )
    assert mesh._absorber_left is absorber1
    assert mesh._absorber_right is absorber2
    assert mesh._absorber_top is absorber1
    assert mesh._absorber_bottom is absorber2

    ##### Invalid combinations

    with pytest.raises(ValueError):
        mw.Mesh2D(
            x=np.linspace(0, 10, 11),
            y=np.linspace(0, 10, 11),
            absorbing_boundary=absorber1,
            absorbing_boundary_left=absorber2,
        )

    with pytest.raises(ValueError):
        mw.Mesh2D(
            x=np.linspace(0, 10, 11),
            y=np.linspace(0, 10, 11),
            absorbing_boundary_x=absorber1,
            absorbing_boundary_left=absorber2,
        )

    with pytest.raises(ValueError):
        mw.Mesh2D(
            x=np.linspace(0, 10, 11),
            y=np.linspace(0, 10, 11),
            absorbing_boundary_y=absorber1,
            absorbing_boundary_top=absorber2,
        )

    with pytest.raises(ValueError):
        mw.Mesh2D(
            x=np.linspace(0, 10, 11),
            y=np.linspace(0, 10, 11),
            absorbing_boundary=absorber1,
            absorbing_boundary_x=absorber2,
        )

    with pytest.raises(ValueError):
        mw.Mesh2D(
            x=np.linspace(0, 10, 11),
            y=np.linspace(0, 10, 11),
            absorbing_boundary=absorber1,
            absorbing_boundary_y=absorber2,
        )


def test_cross_section_n():
    # Test that CrossSection.(n_full, nx, ny, nz) produce correct values
    mesh = mw.Mesh2D(
        x=np.linspace(-5, 5, 200),
        y=np.linspace(-3, 3, 100),
        absorbing_boundary_left=mw.AbsorberParams(
            length=2, end_extinction_coef=0.3, transition_power=3
        ),
        absorbing_boundary_right=mw.AbsorberParams(
            length=1.5, end_extinction_coef=0.5, transition_power=2
        ),
        absorbing_boundary_bottom=mw.AbsorberParams(
            length=0.75, end_extinction_coef=0.4, transition_power=2.5
        ),
    )
    xsec = mw.CrossSection(
        structures=[
            mw.Structure2D(
                geometry=mw.Rectangle(x_min=-1, x_max=1, y_min=-1, y_max=1),
                material=mw.silicon,
            )
        ],
        mesh=mesh,
        env=mw.Environment(),
    )

    for label, x, y, n in [
        ("n_full", mesh.X_full, mesh.Y_full, xsec.n_full()),
        ("nx", mesh.Xx, mesh.Yx, xsec.nx),
        ("ny", mesh.Xy, mesh.Yy, xsec.ny),
        ("nz", mesh.Xz, mesh.Yz, xsec.nz),
    ]:
        left = 0.3 * np.maximum((-3 - x) / 2, 0) ** 3
        right = 0.5 * np.maximum((x - 3.5) / 1.5, 0) ** 2
        bottom = 0.4 * np.maximum((-2.25 - y) / 0.75, 0) ** 2.5
        np.testing.assert_allclose(n.imag, left + right + bottom, err_msg=label)
