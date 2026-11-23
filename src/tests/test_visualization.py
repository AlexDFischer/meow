import itertools
from collections.abc import Iterator
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import ListedColormap

import meow as mw
from meow.mesh import ABSORBER_DEFAULT_RGBA, PML_DEFAULT_RGBA

show = False  # default to not showing if running from pytest

# small list of 3 modes to reuse
test_structures = [
    mw.Structure(
        geometry=mw.Box(
            x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5, z_min=-1, z_max=1
        ),
        material=mw.silicon,
    )
]
test_cell = mw.Cell(
    structures=test_structures,
    z_min=-1,
    z_max=1,
    mesh=mw.Mesh2D(
        x=np.linspace(-2, 2, 50),
        y=np.linspace(-2, 2, 50),
    ),
)
test_xsec = mw.CrossSection.from_cell(cell=test_cell, env=mw.Environment(wl=1.55, T=20))


def _compute_modes_for_test() -> list[mw.Mode]:
    return mw.compute_modes(cs=test_xsec, num_modes=3)


@pytest.fixture(scope="module")
def modes_for_test() -> list[mw.Mode]:
    """Computed once per module, only if a selected test requests it."""
    return _compute_modes_for_test()


@pytest.fixture(autouse=True)
def _close_figures() -> Iterator[None]:
    """Close all figures after each test so tests don't draw on each other's."""
    yield
    plt.close("all")


def test_cell_visualization_no_vacuum():
    """Test cell visualization when there are no vacuum grid points."""
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

    _fig, ax = plt.subplots()
    mw.visualize(cell, show=show, ax=ax)
    ax.set_title("test_cell_visualization_no_vacuum")


def test_cell_visualization_zero_thickness():
    """Test cell visualization when there are structures with zero thickness."""
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

    _fig, ax = plt.subplots()
    mw.visualize(cell, show=show, ax=ax)
    ax.set_title("test_cell_visualization_zero_thickness")


def test_cross_section_visualization_anisotropic():
    """Test cross section visualization for anisotropic materials.

    Make a cross section with some anisotropic material (tidy3d LiNbO3)
    and test that visualize called with index_component='x' or 'y' or 'z'
    results in top of refractive index legend changing according to the component.
    """

    for optical_axis in ["x", "y", "z"]:
        ln = mw.TidyMaterial(
            name="LiNbO3",
            variant="Zelmon1997",
            optical_axis=optical_axis,
        )

        structures = [
            mw.Structure(
                material=ln,
                geometry=mw.Box(
                    x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5, z_min=-1, z_max=1
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
            ),
        )

        env = mw.Environment(wl=1.55, T=20)
        xsec = mw.CrossSection.from_cell(cell=cell, env=env)
        for index_component_vis in ["x", "y", "z"]:
            fig, ax = plt.subplots()
            mw.visualize(
                xsec,
                index_component=index_component_vis,
                ax=ax,
                show=show,
            )
            ax.set_title(
                f"test_cross_section_visualization_anisotropic_{index_component_vis}"
            )

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
                            ln(env, component=index_component_vis),  # ty: ignore[invalid-argument-type]
                        ), (
                            f"Optical axis = {optical_axis}, "
                            f"index component to visualize = {index_component_vis}."
                            f"Colorbar upper limit is {ticks[-1]}, "
                            f"but should be {ln(env, component=index_component_vis)}"  # ty: ignore[invalid-argument-type]
                        )
                        assert np.isclose(
                            ticks[-1],
                            2.14 if index_component_vis == optical_axis else 2.21,
                            rtol=0.01,
                        )


@pytest.mark.parametrize(
    (
        "fields",
        "draw_refractive_index",
        "draw_mode_contours",
        "draw_mode_image",
        "draw_structure_boundaries",
    ),
    [
        (["Ex"], True, True, True, True),
        (["Ex", "Ey"], False, True, False, True),
        (["Ex", "Hx", "Pz"], True, False, True, False),
    ],
)
def test_mode_visualization(
    modes_for_test: list[mw.Mode],
    fields: list[str],
    *,
    draw_refractive_index: bool,
    draw_mode_contours: bool,
    draw_mode_image: bool,
    draw_structure_boundaries: bool,
):
    """Test that mode visualization succeeds for various cases.

    The cases are various combinations of the following:
    - Fields ["Ex"], ["Ex", "Ey"], ["Ex", "Hx", "Pz"]
    - draw_refractive_index True/False
    - draw_mode_contours True/False
    - draw_mode_image True/False
    - draw_structure_boundaries True/False
    """

    mw.visualize(
        modes_for_test[0],
        fields=fields,
        draw_refractive_index=draw_refractive_index,
        draw_mode_contours=draw_mode_contours,
        draw_mode_image=draw_mode_image,
        draw_structure_boundaries=draw_structure_boundaries,
        show=show,
        title_prefix="test_mode_visualization ",
        mode_cmap="rainbow",
    )


@pytest.mark.parametrize(
    "fields",
    [
        (["Ex"]),
        (["Ex", "Ey"]),
        (["Ex", "Hx", "Pz"]),
    ],
)
def test_multiple_modes_visualization(modes_for_test: list[mw.Mode], fields: list[str]):
    """Test that multiple modes visualization succeeds for various arguments."""

    mw.visualize(
        modes_for_test,
        fields=fields,
        draw_refractive_index=True,
        draw_mode_contours=True,
        draw_mode_image=True,
        draw_structure_boundaries=True,
        show=show,
        title_prefix="test_multiple_modes_visualization ",
        mode_cmap="rainbow",
    )


def test_mode_draw_structure_boundaries():
    """Test drawing structures inside and outside the mesh and ensure they appear"""

    # color that doesn't appear elsewhere in the plot so we can
    # programmatically determine whether structure boundary is drawn
    structure_color = "#FF69B4"
    structure_color_rgb = np.array(
        [
            int(f"0x{structure_color[1:3]}", 16),
            int(f"0x{structure_color[3:5]}", 16),
            int(f"0x{structure_color[5:7]}", 16),
        ]
    )

    # make cell with structure fully, partially, or not at all in the mesh
    # then visualize with draw_structure_boundaries=True
    # and check whether structure_color appears in the image accordingly

    #### structure fully in mesh

    fig, ax = plt.subplots()
    cell = mw.Cell(
        structures=test_structures,
        z_min=-1,
        z_max=1,
        mesh=mw.Mesh2D(x=np.linspace(-1, 1, 50), y=np.linspace(-1, 1, 50)),
    )
    xsec = mw.CrossSection.from_cell(cell=cell, env=mw.Environment(wl=1.55, T=20))
    modes = mw.compute_modes(cs=xsec, num_modes=1)
    mw.visualize(
        modes[0],
        fields=["Ex"],
        draw_mode_contours=True,
        draw_mode_image=False,
        draw_structure_boundaries=True,
        structure_boundaries_color=structure_color,
        ax=ax,
        show=False,
    )
    # check that structure_color appears in the image
    fig.canvas.draw()
    img = np.array(fig.canvas.renderer.buffer_rgba())  # ty: ignore[unresolved-attribute]

    if show:
        plt.show()

    assert np.any(np.all(img[:, :, :3] == structure_color_rgb, axis=-1))

    #### structure partially in mesh

    fig, ax = plt.subplots()
    cell = mw.Cell(
        structures=test_structures,
        z_min=-1,
        z_max=1,
        mesh=mw.Mesh2D(x=np.linspace(-2, 0, 50), y=np.linspace(-2, 0, 50)),
    )
    xsec = mw.CrossSection.from_cell(cell=cell, env=mw.Environment(wl=1.55, T=20))
    modes = mw.compute_modes(cs=xsec, num_modes=1)
    mw.visualize(
        modes[0],
        fields=["Ex"],
        draw_mode_contours=True,
        draw_mode_image=False,
        draw_structure_boundaries=True,
        structure_boundaries_color=structure_color,
        ax=ax,
        show=False,
    )
    fig.canvas.draw()
    img = np.array(fig.canvas.renderer.buffer_rgba())  # ty: ignore[unresolved-attribute]

    if show:
        plt.show()

    assert np.any(np.all(img[:, :, :3] == structure_color_rgb, axis=-1))

    # test that plot boundaries are correct, as plotting structure boundaries
    # outside plot can mess things up if you're not careful
    # with some tolerance because the limits get changed to min and max of mesh
    assert np.isclose(ax.get_xlim()[0], -2, atol=0.05), (
        f"{ax.get_xlim()[0] = }, should be near -2"
    )
    assert np.isclose(ax.get_xlim()[1], 0, atol=0.05), (
        f"{ax.get_xlim()[1] = }, should be near 0"
    )
    assert np.isclose(ax.get_ylim()[0], -2, atol=0.05), (
        f"{ax.get_ylim()[0] = }, should be near -2"
    )
    assert np.isclose(ax.get_ylim()[1], 0, atol=0.05), (
        f"{ax.get_ylim()[1] = }, should be near 0"
    )

    ##### structure outside of mesh

    fig, ax = plt.subplots()
    cell = mw.Cell(
        structures=test_structures,
        z_min=-1,
        z_max=1,
        mesh=mw.Mesh2D(x=np.linspace(2, 3, 50), y=np.linspace(2, 3, 50)),
    )
    xsec = mw.CrossSection.from_cell(cell=cell, env=mw.Environment(wl=1.55, T=20))
    modes = mw.compute_modes(cs=xsec, num_modes=1)
    mw.visualize(
        modes[0],
        fields=["Ex"],
        draw_mode_contours=True,
        draw_mode_image=False,
        draw_structure_boundaries=True,
        structure_boundaries_color=structure_color,
        ax=ax,
        show=False,
    )
    fig.canvas.draw()
    img = np.array(fig.canvas.renderer.buffer_rgba())  # ty: ignore[unresolved-attribute]

    if show:
        plt.show()

    assert not np.any(np.all(img[:, :, :3] == structure_color_rgb, axis=-1))

    # test that plot boundaries are correct, as plotting structure boundaries
    # outside plot can mess things up if you're not careful
    # with some tolerance because the limits get changed to min and max of mesh
    assert np.isclose(ax.get_xlim()[0], 2, atol=0.05), (
        f"{ax.get_xlim()[0] = }, should be near 2"
    )
    assert np.isclose(ax.get_xlim()[1], 3, atol=0.05), (
        f"{ax.get_xlim()[1] = }, should be near 3"
    )
    assert np.isclose(ax.get_ylim()[0], 2, atol=0.05), (
        f"{ax.get_ylim()[0] = }, should be near 2"
    )
    assert np.isclose(ax.get_ylim()[1], 3, atol=0.05), (
        f"{ax.get_ylim()[1] = }, should be near 3"
    )


@pytest.mark.parametrize("cross_section", [False, True], ids=["cell", "cross_section"])
@pytest.mark.parametrize("draw_mesh", [False, True], ids=["no_mesh", "primal_mesh"])
def test_pml_visualization(*, cross_section: bool, draw_mesh: bool) -> None:
    """A single PML layer is visible along each edge away from the corners."""
    mesh = mw.Mesh2D(x=np.arange(7), y=np.arange(7), num_pml=(1, 1))
    cell = mw.Cell(structures=[], mesh=mesh, z_min=0, z_max=1)
    obj = (
        mw.CrossSection.from_cell(cell=cell, env=test_xsec.env)
        if cross_section
        else cell
    )
    fig, ax = plt.subplots()
    ax.set_facecolor("white")
    mw.visualize(
        obj,
        ax=ax,
        cbar=False,
        show=False,
        draw_pml=True,
        draw_mesh=draw_mesh,
        n_cmap=ListedColormap(["white"]),
    )
    ax.grid(visible=False)
    fig.canvas.draw()
    assert ax.get_xlim() == (mesh.x[0], mesh.x_[-1])
    assert ax.get_ylim() == (mesh.y[0], mesh.y_[-1])
    assert len(ax.lines) == (len(mesh.x) + len(mesh.y) if draw_mesh else 0)
    # Flip the image so its row coordinates match Matplotlib's display coordinates.
    img = np.asarray(fig.canvas.renderer.buffer_rgba())[::-1, :, :3]  # ty: ignore[unresolved-attribute]
    red, green, blue, alpha = PML_DEFAULT_RGBA
    expected_rgb = 255 * (alpha * np.array([red, green, blue]) + (1 - alpha))

    edge_interiors = {
        "left": ((0.25, 2), (0.75, 4)),
        "right": ((5.125, 2), (5.375, 4)),
        "bottom": ((2, 0.25), (4, 0.75)),
        "top": ((2, 5.125), (4, 5.375)),
    }
    for edge, bounds in edge_interiors.items():
        (x0, y0), (x1, y1) = np.rint(ax.transData.transform(bounds)).astype(int)
        pixels = img[y0:y1, x0:x1]
        matches = np.all(np.isclose(pixels, expected_rgb, atol=2, rtol=0), axis=-1)
        assert matches.any(), f"No PML-colored pixels along the {edge} edge"


@pytest.mark.parametrize("draw_pml", [False, True], ids=["no_pml", "pml"])
@pytest.mark.parametrize(
    "draw_absorbers", [False, True], ids=["no_absorbers", "absorbers"]
)
def test_cross_section_boundary_colors(*, draw_pml: bool, draw_absorbers: bool) -> None:
    """Each enabled overlay contributes its default color over white vacuum."""
    # Use thinner PML bands on x and wider absorber bands on y so each
    # overlay has a region of white vacuum to itself even when both are drawn.
    mesh = mw.Mesh2D(
        x=np.linspace(-4, 4, 17),
        y=np.linspace(-4, 4, 17),
        num_pml=(1, 0),
        absorbing_boundary_y=mw.AbsorberParams(length=1.5),
    )
    cell = mw.Cell(structures=test_structures, mesh=mesh, z_min=-1, z_max=1)
    cross_section = mw.CrossSection.from_cell(cell=cell, env=test_xsec.env)
    fig, ax = plt.subplots(facecolor="white")
    mw.visualize(
        cross_section,
        ax=ax,
        cbar=False,
        show=False,
        n_cmap=ListedColormap(["white", "blue"]),
        draw_pml=draw_pml,
        draw_absorbers=draw_absorbers,
    )
    # Antialiased axis decorations can match the blended overlay colors.
    ax.set_axis_off()
    fig.canvas.draw()
    pixels = np.asarray(fig.canvas.renderer.buffer_rgba())[:, :, :3]  # ty: ignore[unresolved-attribute]

    for name, rgba, enabled in (
        ("PML", PML_DEFAULT_RGBA, draw_pml),
        ("adiabatic absorber", ABSORBER_DEFAULT_RGBA, draw_absorbers),
    ):
        red, green, blue, alpha = rgba
        expected_rgb = 255 * (alpha * np.array([red, green, blue]) + (1 - alpha))
        matches = np.all(np.isclose(pixels, expected_rgb, atol=2, rtol=0), axis=-1)
        assert bool(matches.any()) == enabled, f"Unexpected {name} color visibility"


def _layered_cross_section(indices: list[float]) -> mw.CrossSection:
    """Horizontal layers of constant-index materials stacked in y, in vacuum."""
    structures = [
        mw.Structure(
            material=mw.IndexMaterial(name=f"layer{i}", n=n),
            geometry=mw.Box(
                x_min=-1,
                x_max=1,
                y_min=-1 + 0.3 * i,
                y_max=-0.7 + 0.3 * i,
                z_min=-1,
                z_max=1,
            ),
        )
        for i, n in enumerate(indices)
    ]
    cell = mw.Cell(
        structures=structures,
        z_min=-1,
        z_max=1,
        mesh=mw.Mesh2D(x=np.linspace(-1.5, 1.5, 61), y=np.linspace(-1.5, 1.5, 61)),
    )
    return mw.CrossSection.from_cell(cell=cell, env=mw.Environment())


def _colorbar_ticks(fig: plt.Figure) -> tuple[list[float], list[str]]:
    """Draw the figure and return its colorbar's tick positions and labels."""
    # Not `fig.canvas.draw()`: when run with `show = True`, closing the window
    # makes the figure go stale and getting ticks fails.
    fig.draw_without_rendering()
    # Drawing must leave the figure clean; ticks changed during a draw mark it
    # stale and trigger another redraw. Checked before reading the labels:
    # get_yticklabels() itself marks it stale.
    assert not fig.stale
    cax = fig.axes[-1]  # the colorbar axes is appended last
    labels = [label.get_text() for label in cax.get_yticklabels()]
    return list(cax.get_yticks()), labels


def test_cross_section_colorbar_ticks_each_material_index():
    """The colorbar ticks each material's index, and keeps doing so on redraw."""
    xs = _layered_cross_section([1.444, 3.476])
    fig, ax = plt.subplots(figsize=(6, 6))
    mw.visualize(xs, ax=ax, show=show)

    for _ in range(2):  # the first draw used to replace the ticks
        ticks, labels = _colorbar_ticks(fig)
        np.testing.assert_allclose(ticks, [1.0, 1.444, 3.476])
        assert labels == ["1.000", "1.444", "3.476"]


def test_cross_section_colorbar_ticks_keep_extremes_when_crowded():
    """On a short colorbar with close indices, ticks are thinned but the lowest
    and highest indices are always kept."""
    indices = [1.44, 1.45, 1.46, 1.47, 2.0, 3.47, 3.48]
    xs = _layered_cross_section(indices)
    fig, ax = plt.subplots(figsize=(3, 1.5))
    mw.visualize(xs, ax=ax, show=show)

    ticks, _ = _colorbar_ticks(fig)
    all_values = [1.0, *indices]
    assert ticks[0] == pytest.approx(min(all_values))
    assert ticks[-1] == pytest.approx(max(all_values))
    assert len(ticks) < len(all_values)
    assert all(any(np.isclose(t, v) for v in all_values) for t in ticks)


def test_cross_section_colorbar_ticks_spatially_varying():
    """A spatially varying material gives round, evenly spaced ticks, not one
    per distinct index."""
    material = mw.SpatiallyVaryingMaterial(
        name="ramp",
        n=lambda x, y, z: 2.0 + 0.5 * x,  # noqa: ARG005
    )
    structure = mw.Structure(
        material=material,
        geometry=mw.Box(x_min=-1, x_max=1, y_min=-1, y_max=1, z_min=-1, z_max=1),
    )
    cell = mw.Cell(
        structures=[structure],
        z_min=-1,
        z_max=1,
        mesh=mw.Mesh2D(x=np.linspace(-1.5, 1.5, 61), y=np.linspace(-1.5, 1.5, 61)),
    )
    xs = mw.CrossSection.from_cell(cell=cell, env=mw.Environment())
    fig, ax = plt.subplots(figsize=(6, 6))
    mw.visualize(xs, ax=ax, show=show)

    ticks, _ = _colorbar_ticks(fig)
    steps = np.diff(ticks)
    assert 2 <= len(ticks) <= 12
    np.testing.assert_allclose(steps, steps[0])  # evenly spaced
    # round values: every tick is a multiple of the step
    assert all(np.isclose(t / steps[0], round(t / steps[0])) for t in ticks)


def _colorbar_axes_of(ax: plt.Axes) -> plt.Axes:
    """The axes of the colorbar drawn for the data plotted on ``ax``."""
    cbars = [artist.colorbar for artist in [*ax.collections, *ax.images]]
    [cbar] = [c for c in cbars if c is not None]
    return cbar.ax


def _tight(artist: plt.Axes, renderer: object) -> Any:
    """``artist``'s tight bounding box (tick labels included), in pixels."""
    bbox = artist.get_tightbbox(renderer)  # ty: ignore[invalid-argument-type]
    assert bbox is not None
    return bbox


def _assert_colorbars_fit(fig: plt.Figure, axs: list) -> None:
    """Check each panel's colorbar against a constrained-layout row of panels.

    The layout rect is untouched, each colorbar (tick labels included) ends
    before the next panel begins, and the last one ends inside the figure.
    """
    fig.draw_without_rendering()
    engine = fig.get_layout_engine()
    assert engine is not None
    assert engine.get()["rect"] == (0, 0, 1, 1)
    renderer = fig.canvas.get_renderer()  # ty: ignore[unresolved-attribute]
    for ax, next_ax in itertools.pairwise(axs):
        cax = _colorbar_axes_of(ax)
        assert _tight(cax, renderer).x1 <= _tight(next_ax, renderer).x0
    cax = _colorbar_axes_of(axs[-1])
    assert _tight(cax, renderer).x1 <= fig.bbox.x1


# In the constrained-layout tests below, never show between panels: closing the
# window destroys the figure's GUI canvas, and drawing the next panel into it
# then fails. Draw every panel, check, then show once.


def test_cross_section_colorbars_in_constrained_layout():
    """Cross-section colorbars in a constrained-layout figure neither shrink the
    layout nor collide with the neighbouring subplot.
    """
    xs = _layered_cross_section([1.444, 3.476])
    fig, axs = plt.subplots(1, 4, figsize=(12, 3), layout="constrained")
    for ax in axs:
        mw.visualize(xs, ax=ax, show=False)
    _assert_colorbars_fit(fig, list(axs))
    if show:
        plt.show()


def test_cell_colorbars_in_constrained_layout():
    """Cell colorbars, labelled with material names, fit in a constrained row.

    Regression test: the names (e.g. 'vacuum') overlapped the next subplot.
    """
    xs = _layered_cross_section([1.444, 3.476])
    cell = xs._cell
    assert cell is not None
    fig, axs = plt.subplots(1, 3, figsize=(10, 3), layout="constrained")
    for ax in axs:
        mw.visualize(cell, ax=ax, show=False)
    _assert_colorbars_fit(fig, list(axs))
    if show:
        plt.show()


def test_mode_colorbars_in_constrained_layout(modes_for_test: list[mw.Mode]):
    """Mode field colorbars fit in a narrow constrained-layout row."""
    fig, axs = plt.subplots(1, 3, figsize=(9, 2.6), layout="constrained")
    mw.visualize(modes_for_test[0], fields=["Ex", "Hx", "Pz"], ax=axs, show=False)
    _assert_colorbars_fit(fig, list(axs))
    if show:
        plt.show()


def test_mode_grid_colorbar_labels_fit_on_first_draw(modes_for_test: list[mw.Mode]):
    """meow's own grid of modes x fields keeps every colorbar label inside the
    figure after a single draw (as in ``savefig``).

    Regression test: with constrained layout, a grid of fixed-aspect plots
    needed several draws to settle, so the right-hand colorbar labels were cut
    off at the figure edge on the first one.
    """
    mw.visualize(modes_for_test, fields=["Ex", "Hy"], show=False)
    fig = plt.gcf()
    fig.draw_without_rendering()
    renderer = fig.canvas.get_renderer()  # ty: ignore[unresolved-attribute]
    for ax in fig.axes:
        if ax.images or ax.collections:  # a field panel, not a colorbar
            cax = _colorbar_axes_of(ax)
            assert _tight(cax, renderer).x1 <= fig.bbox.x1
    if show:
        plt.show()


if __name__ == "__main__":
    show = True  # show figures if running from command line
    modes = _compute_modes_for_test()

    # run tests with a subset of parameter values
    test_cell_visualization_no_vacuum()
    test_cell_visualization_zero_thickness()
    test_cross_section_visualization_anisotropic()
    test_mode_visualization(
        modes,
        fields=["Ex", "Hx", "Pz"],
        draw_refractive_index=True,
        draw_mode_contours=False,
        draw_mode_image=True,
        draw_structure_boundaries=False,
    )
    test_multiple_modes_visualization(modes, fields=["Ex", "Hx", "Pz"])
    test_mode_draw_structure_boundaries()
    test_cross_section_colorbar_ticks_each_material_index()
    test_cross_section_colorbar_ticks_keep_extremes_when_crowded()
    test_cross_section_colorbar_ticks_spatially_varying()
    test_cross_section_colorbars_in_constrained_layout()
    test_cell_colorbars_in_constrained_layout()
    test_mode_colorbars_in_constrained_layout(modes)
    test_mode_grid_colorbar_labels_fit_on_first_draw(modes)
