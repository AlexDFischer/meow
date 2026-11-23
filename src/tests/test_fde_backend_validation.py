"""Verify unsupported inputs are rejected without optional FDE solvers."""

from collections.abc import Callable

import numpy as np
import pytest

import meow as mw


@pytest.mark.parametrize(
    ("solve", "feature", "message"),
    [
        (solve, feature, message)
        for solve in (mw.compute_modes_meep, mw.compute_modes_lumerical)
        for feature, message in (
            ("absorber", "adiabatic absorbers"),
            ("anisotropy", "anisotropic material"),
            ("spatial_index", "spatially varying material"),
        )
    ]
    + [
        (mw.compute_modes_meep, "pml", "num_pml"),
        (mw.compute_modes_meep, "loss", "complex index"),
    ],
)
def test_unsupported_fde_inputs(solve: Callable, feature: str, message: str):
    mesh = mw.Mesh2D(
        x=np.linspace(-1, 1, 5),
        y=np.linspace(-1, 1, 5),
        absorbing_boundary_top=mw.AbsorberParams(length=0.5)
        if feature == "absorber"
        else None,
        num_pml=(1, 0) if feature == "pml" else (0, 0),
    )
    material = mw.IndexMaterial(name="scalar", n=2 + 0.1j if feature == "loss" else 2)
    if feature == "anisotropy":
        material = mw.AnisotropicIndexMaterial(name="tensor", nx=2, ny=3, nz=4)
    if feature == "spatial_index":
        material = mw.SpatiallyVaryingMaterial(name="graded", n=lambda x, _y, _z: 2 + x)
    cell = mw.Cell(
        mesh=mesh,
        structures=[
            mw.Structure(
                geometry=mw.Box(
                    x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5, z_min=-1, z_max=1
                ),
                material=material,
            )
        ],
        z_min=0,
        z_max=0,
    )
    cs = mw.CrossSection.from_cell(cell=cell, env=mw.Environment(wl=1.55))

    with pytest.raises(NotImplementedError, match=message):
        solve(cs)
