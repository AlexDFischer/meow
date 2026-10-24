import matplotlib.pyplot as plt
import numpy as np

import meow as mw

# Ensure that cell visualization does not crash with a few edge cases:
# no vacuum grid points, structures with zero thickness


def test_cell_visualization_no_vacuum():
    structures = [
        mw.Structure(
            material=mw.silicon,
            geometry=mw.Box(
                x_min=-0.225, x_max=+0.225, y_min=0, y_max=0.22, z_min=-1, z_max=+1
            ),
            mesh_order=1,
        ),
        mw.Structure(
            material=mw.silicon_oxide,
            geometry=mw.Box(x_min=-1, x_max=+1, y_min=-1, y_max=+1, z_min=-1, z_max=+1),
            mesh_order=2,
        ),
    ]

    cell = mw.Cell(
        structures=structures,
        z_min=0,
        z_max=0,
        mesh=mw.Mesh2D(x=np.linspace(-1, 1, 100), y=np.linspace(-1, 1, 100)),
    )

    mw.visualize(cell, show=False)


def test_cell_visualization_zero_thickness():
    structures = [
        mw.Structure(
            material=mw.silicon,
            geometry=mw.Box(
                x_min=-0.225, x_max=+0.225, y_min=0, y_max=0, z_min=-1, z_max=+1
            ),
            mesh_order=1,
        ),
        mw.Structure(
            material=mw.silicon_oxide,
            geometry=mw.Box(x_min=-1, x_max=+1, y_min=-1, y_max=0, z_min=-1, z_max=+1),
            mesh_order=2,
        ),
    ]

    cell = mw.Cell(
        structures=structures,
        z_min=0,
        z_max=0,
        mesh=mw.Mesh2D(x=np.linspace(-1, 1, 100), y=np.linspace(-1, 1, 100)),
    )

    mw.visualize(cell, show=False)

def test_cross_section_visualization_anisotropic():
    # make a cross section with some anisotopic material (tidy3d LiNbO3)
    # and test that visualize called with index_component='x' or 'y' or 'z'
    # results in top of refractive index legend changing according to the component.

    for optical_axis in ['x', 'y', 'z']:
        ln = mw.TidyMaterial(name='LiNbO3', variant='Zelmon1997', optical_axis=optical_axis,)

        structures = [
            mw.Structure(
                material=ln,
                geometry=mw.Box(
                    x_min=-0.5,
                    x_max=0.5,
                    y_min=-0.5,
                    y_max=0.5,
                    z_min=-1,
                    z_max=1
                ),
                mesh_order=1,
            )
        ]

        cell = mw.Cell(
            structures=structures,
            z_min=0,
            z_max=0,
            mesh=mw.Mesh2D(
                x=np.linspace(-2, 2, 100),
                y=np.linspace(-2, 2, 100),
            )

        )

        env = mw.Environment(wl=1.55, T=20)
        xsec = mw.CrossSection.from_cell(cell=cell, env=env)
        for index_component_vis in ['x', 'y', 'z']:
            fig, ax = plt.subplots()
            mw.visualize(xsec, index_component=index_component_vis, ax=ax, show=False)

            # find  colorbar of the visualized cross section,
            # and verify that the upper limit is that of the
            # refractive index of LiNbO3 along index_component_vis
            for ax in fig.axes:
                for collection in ax.collections:
                    cbar = collection.colorbar
                    if cbar is not None:
                        ticks = cbar.get_ticks()

                        assert np.isclose(
                            ticks[-1],
                            ln(env, component=index_component_vis)
                        ), f"Optical axis = {optical_axis}, index component to visualize = {index_component_vis}." \
                            f"Colorbar upper limit is {ticks[-1]}, but should be {ln(env, component=index_component_vis)}"
                        assert np.isclose(
                            ticks[-1],
                            2.14 if index_component_vis == optical_axis else 2.21,
                            rtol=0.01
                        )