from functools import partial
import numpy as np
import pandas as pd
from pathlib import Path

import meow as mw

si = mw.TidyMaterial(name="cSi", variant="Li1993_293K")
sio2 = mw.TidyMaterial(name="SiO2", variant="Palik_LowLoss")
si_n = mw.TidyMaterial(name="Si3N4", variant="Luke2015PMLStable")
env = mw.Environment(T=20, wl=1.55)

visualize = False # Set to True to visualize results

def test_evanescent_coupler_matches_tidy3d():
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_evanescent_coupler_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example
    
    silicon_height = 0.22
    waveguide_width = 0.45
    waveguide_gap = 0.2

    x_min = -3 * waveguide_width
    x_max = +3 * waveguide_width
    y_min = -silicon_height / 2 - 2 * waveguide_width
    y_max = +silicon_height / 2 + 2 * waveguide_width

    structures = [
        mw.Structure( # cladding
            material=sio2,
            geometry=mw.Box(
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                z_min=0,
                z_max=3
            ),
            mesh_order=2,
        ),
        mw.Structure( # left waveguide
            material=si,
            geometry=mw.Box(
                x_min=-waveguide_width - waveguide_gap / 2,
                x_max=-waveguide_gap / 2,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=0,
                z_max=2,
            ),
            mesh_order=1,
        ),
        mw.Structure( # right waveguide
            material=si,
            geometry=mw.Box(
                x_min=waveguide_gap / 2,
                x_max=waveguide_gap / 2 + waveguide_width,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=1,
                z_max=3,
            ),
            mesh_order=1,
        ),
    ]

    dl =  0.010
    mesh = mw.Mesh2D(
        x=np.arange(x_min, x_max, dl),
        y=np.arange(y_min, y_max, dl)
    )

    cells = mw.create_cells(
        structures=structures,
        mesh=mesh,
        Ls=np.array([1, 1, 1]),
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_modes = [1, 2, 1]  # number of modes to compute for each cross-section
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    S_matrix, _port_map = mw.compute_s_matrix(modes=modes,
                        cells=cells)

    interaction_length_arr = np.linspace(0, 50, 100)
    cell_lengths_arr = [[1, length, 1] for length in interaction_length_arr]
    coupling_00_arr = []

    for cell_lengths in cell_lengths_arr:
        S_matrix, _port_map = mw.compute_s_matrix(modes=modes, cell_lengths=cell_lengths)
        coupling_00_arr.append(np.abs(S_matrix[0][1])**2)

    meow_tidy3d_diff = np.abs(np.array(coupling_00_arr) - tidy3d_results.coupling_00)
    max_diff = np.max(np.abs(meow_tidy3d_diff))

    if visualize:
        from matplotlib import pyplot as plt

        _fig, ax = plt.subplots(layout='constrained', dpi=300)

        ax.plot(tidy3d_results.length, tidy3d_results.coupling_00, label="Coupling (Tidy3D)", linestyle="dotted", linewidth=2)
        ax.plot(interaction_length_arr, coupling_00_arr, label="Coupling (MEOW)", linestyle="solid", linewidth=0.5)
        ax.legend()
        ax.set_xlabel("Interaction length (um)")
        ax.set_ylabel("Coupling")
        ax.set_title(f"Coupling vs interaction length. Max diff {max_diff:.5f}")
        plt.show()

    if max_diff > 0.01:
        error_msg = f"MEOW results do not closely match Tidy3D results. Max difference: {max_diff}"
        raise AssertionError(error_msg)

def test_mmi_matches_tidy3d():
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_mmi_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example

    silicon_height = 0.22
    width_mmi = 8.0
    length_mmi = 57.5
    waveguide_width = 1.5
    cladding_buffer = 1.0
    output_waveguide_offset = 2.0
    dl = 0.020

    x_min = -width_mmi / 2 - cladding_buffer
    x_max = +width_mmi / 2 + cladding_buffer
    y_min = -silicon_height / 2 - cladding_buffer
    y_max = +silicon_height / 2 + cladding_buffer

    structures = [
        mw.Structure( # cladding
            material=sio2,
            geometry=mw.Box(
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                z_min=0,
                z_max=length_mmi + 2
            ),
            mesh_order=2,
        ),
        mw.Structure( # input waveguide
            material=si,
            geometry=mw.Box(
                x_min=-waveguide_width / 2,
                x_max=+waveguide_width / 2,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=0,
                z_max=1,
            ),
            mesh_order=1,
        ),
        mw.Structure( # MMI section
            material=si,
            geometry=mw.Box(
                x_min=-width_mmi / 2,
                x_max=+width_mmi / 2,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=1,
                z_max=length_mmi + 1,
            ),
            mesh_order=1,
        ),
        mw.Structure( # top output waveguide
            material=si,
            geometry=mw.Box(
                x_min=+output_waveguide_offset - waveguide_width / 2,
                x_max=+output_waveguide_offset + waveguide_width / 2,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=length_mmi + 1,
                z_max=length_mmi + 2,
            ),
            mesh_order=1,
        ),
        mw.Structure( # bottom output waveguide
            material=si,
            geometry=mw.Box(
                x_min=-output_waveguide_offset - waveguide_width / 2,
                x_max=-output_waveguide_offset + waveguide_width / 2,
                y_min=-silicon_height / 2,
                y_max=silicon_height / 2,
                z_min=length_mmi + 1,
                z_max=length_mmi + 2,
            ),
            mesh_order=1,
        ),
    ]

    cells = mw.create_cells(
        structures=structures,
        mesh=mw.Mesh2D(
            x=np.arange(x_min, x_max, dl),
            y=np.arange(y_min, y_max, dl),
        ),
        Ls=np.array([1, length_mmi, 1]),
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_mmi_modes = 15
    num_modes = [1, num_mmi_modes, 1]
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    if visualize:
        from matplotlib import pyplot as plt

        mw.visualize(modes[2][0], fields=['Ex'], operation=np.real)

        z_arr = np.linspace(0, length_mmi + 2, 1000)
        field, x = mw.propagate_modes(modes, cells, y=0, z=z_arr)

        _fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.pcolormesh(z_arr, x, np.abs(field).T, shading="auto", cmap="magma")
        ax.set_xlabel("z [um]")
        ax.set_ylabel("x [um]")
        ax.set_title("|Ex(x, z)| from mw.propagate_modes")
        plt.colorbar(im, ax=ax, label="|Ex|")
        plt.tight_layout()
        plt.show()

    output_coupling_symmetric_mode_arr = []
    length_arr = np.linspace(40, 80, 100)
    for length in length_arr:
        S_matrix, _port_map = mw.compute_s_matrix(modes=modes, cell_lengths=[1, length, 1])
        output_coupling_symmetric_mode_arr.append(np.abs(S_matrix[0][1])**2)

    meow_tidy3d_diff = np.abs(np.array(output_coupling_symmetric_mode_arr) - tidy3d_results.coupling_00)
    max_diff = np.max(np.abs(meow_tidy3d_diff))

    if visualize:
        _fig, ax = plt.subplots(layout='constrained', dpi=300)

        ax.plot(tidy3d_results.length, tidy3d_results.coupling_00, label="Coupling (Tidy3D)", linestyle="dotted", linewidth=2)
        ax.plot(length_arr, output_coupling_symmetric_mode_arr, label="Coupling (MEOW)", linestyle="solid", linewidth=0.5)
        ax.legend()
        ax.set_xlabel("MMI length (um)")
        ax.set_ylabel("Coupling to symmetric output mode")
        ax.set_title(f"Coupling vs MMI length. Max diff {max_diff:.5f}")
        plt.show()

    if max_diff > 0.01:
        error_msg = f"MEOW results do not closely match Tidy3D results. Max difference: {max_diff}"
        raise AssertionError(error_msg)

def test_taper_matches_tidy3d():
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_taper_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example

    silicon_height = 0.22
    waveguide_width_start = 0.45
    waveguide_width_end = 1.5
    taper_length = 20.0
    cladding_buffer = 1.0
    dl = 0.020

    x_min = -waveguide_width_end / 2 - cladding_buffer
    x_max = +waveguide_width_end / 2 + cladding_buffer
    y_min = -silicon_height / 2 - cladding_buffer
    y_max = +silicon_height / 2 + cladding_buffer

    num_cells = 30
    num_modes_per_cell = 5

    structures = [
                mw.Structure( # cladding
                    material=sio2,
                    geometry=mw.Box(
                        x_min=x_min,
                        x_max=x_max,
                        y_min=y_min,
                        y_max=y_max,
                        z_min=0,
                        z_max=taper_length
                    ),
                    mesh_order=2,
                ),
    ]

    for i in range(num_cells):
        # linearly interpolate waveguide width for this cell
        waveguide_width = waveguide_width_start + (waveguide_width_end - waveguide_width_start) * (i / (num_cells - 1))

        structures.append(
            mw.Structure(
                material=si,
                geometry=mw.Box(
                    x_min=-waveguide_width / 2,
                    x_max=+waveguide_width / 2,
                    y_min=-silicon_height / 2,
                    y_max=silicon_height / 2,
                    z_min=i * taper_length / num_cells,
                    z_max=(i + 1) * taper_length / num_cells,
                ),
                mesh_order=1,
            ),
        )

    cells = mw.create_cells(
        structures=structures,
        mesh=mw.Mesh2D(
            x=np.arange(x_min, x_max, dl),
            y=np.arange(y_min, y_max, dl),
        ),
        Ls=np.array([taper_length / num_cells for _ in range(num_cells)]),
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_modes = [1] + [num_modes_per_cell] * (num_cells - 1)
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    # only plot even modes, as those are the only ones that
    # should couple to the even fundamental mode that we excite
    modes_to_compare_and_plot = [0, 2, 4]

    if visualize:
        # visualize propagation
        from matplotlib import pyplot as plt

        z_arr = np.linspace(0, taper_length, 500)
        field, x = mw.propagate_modes(modes, cells, y=0, z=z_arr)

        _fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.pcolormesh(z_arr, x, np.abs(field).T, shading="auto", cmap="magma")
        ax.set_xlabel("z [um]")
        ax.set_ylabel("x [um]")
        ax.set_title("|Ex(x, z)| from mw.propagate_modes")
        plt.colorbar(im, ax=ax, label="|Ex|")
        plt.tight_layout()
        plt.show()

    output_mode_to_coupling_arr = {output_mode: [] for output_mode in modes_to_compare_and_plot}

    length_arr = np.linspace(0, 10, 45)
    for length in length_arr:
        S_matrix, _port_map = mw.compute_s_matrix(modes=modes, cell_lengths=[length / num_cells for _ in range(num_cells)])
        for output_mode in modes_to_compare_and_plot:
            output_mode_to_coupling_arr[output_mode].append(np.abs(S_matrix[0][1 + output_mode])**2)

    meow_tidy3d_diff = np.max([
        np.abs(np.array(output_mode_to_coupling_arr[output_mode]) - tidy3d_results[f'coupling_0{output_mode}']) for output_mode in modes_to_compare_and_plot
    ])
    max_diff = np.max(np.abs(meow_tidy3d_diff))

    if visualize:
        _fig, ax = plt.subplots(layout='constrained', dpi=300)

        for output_mode, coupling_arr in output_mode_to_coupling_arr.items():
            ax.plot(tidy3d_results.length,
                    tidy3d_results[f'coupling_0{output_mode}'],
                    label=f"Mode 0 -> {output_mode} coupling (Tidy3D)",
                    linestyle="dotted", linewidth=2)
            ax.plot(length_arr,
                    coupling_arr,
                    label=f"Mode 0 -> {output_mode} coupling (MEOW)",
                    linestyle="solid",
                    linewidth=0.5)
        ax.legend()
        ax.set_xlabel("Taper length (um)")
        ax.set_ylabel("Coupling to output modes")
        ax.set_title(f"Coupling vs taper length. Max diff {max_diff:.5f}")
        plt.show()

    if max_diff > 0.01:
        error_msg = f"MEOW results do not closely match Tidy3D results. Max difference: {max_diff}"
        raise AssertionError(error_msg)

def test_bend_matches_tidy3d():
    """Tests a circular bend. This makes 3 cells: one input cell that's straight, then one bent cell, then one straight cell.
    This test examines the coupling to higher order modes after the bent region and compares to Tidy3D results.

    Args:
    Returns:
        None
    """
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_bend_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    min_bend_radius = 20
    max_bend_radius = 40
    num_sweep_points = 11
    bend_radius_arr = np.linspace(min_bend_radius, max_bend_radius, num_sweep_points)

    num_cells = 3
    num_modes_arr = [1, 1, 5]

    # structure is just a straight waveguide
    # we manually modify the bend radius in each cell

    waveguide_height = 0.5
    waveguide_width = 2.0
    waveguide_length = 3
    cladding_buffer_horizontal = 2.0
    cladding_buffer_vertical = 0.8
    dl = 0.05

    x_min = -waveguide_width / 2 - cladding_buffer_horizontal
    x_max = +waveguide_width / 2 + cladding_buffer_horizontal
    y_min = -waveguide_height / 2 - cladding_buffer_vertical
    y_max = +waveguide_height / 2 + cladding_buffer_vertical

    waveguide = mw.Structure(
        material=si_n,
        geometry=mw.Box(
            x_min=-waveguide_width / 2,
            x_max=+waveguide_width / 2,
            y_min=-waveguide_height / 2,
            y_max=+waveguide_height / 2,
            z_min=0,
            z_max=waveguide_length
        ),
        mesh_order=1
    )
    cladding = mw.Structure(
        material=sio2,
        geometry=mw.Box(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            z_min=0,
            z_max=waveguide_length,
        ),
        mesh_order=2
    )

    cells = []

    # sweep bend radius

    modes_to_compare_and_plot = [0, 1, 2,]
    # dict of lists. The dict key is the mode index, and the value is a list of couplings for that mode across different bend radii
    mode_index_bend_radius_to_couplings: dict[list[float]] = {mode_index : [] for mode_index in modes_to_compare_and_plot}

    for bend_radius in bend_radius_arr:
        cells = []
        for cell_bend_radius in [None, bend_radius, None]:
            cells.append(
                mw.Cell(
                    structures=[waveguide, cladding],
                    z_min=0,
                    z_max=1,
                    mesh=mw.Mesh2D(
                        x=np.arange(x_min, x_max, dl),
                        y=np.arange(y_min, y_max, dl),
                        bend_radius=cell_bend_radius,
                        bend_axis=1,
                        num_pml=(10, 10),
                    ),
                )
            )

        xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
        modes = [mw.compute_modes(cs=xsec, num_modes=num_modes_arr[i]) for i, xsec in enumerate(xsecs)]

        S_matrix, _port_map = mw.compute_s_matrix(
            modes=modes,
            cells=cells,
            interfaces_fn=partial(
                mw.compute_interface_s_matrices,
                passivity_method='clip',
            ),
        )
        for output_mode in modes_to_compare_and_plot:
            if len(S_matrix[0]) > 1 + output_mode:
                mode_index_bend_radius_to_couplings[output_mode].append(np.abs(S_matrix[0][1 + output_mode])**2)
            else:
                mode_index_bend_radius_to_couplings[output_mode].append(None)

    meow_tidy3d_diff = np.max([
        np.abs(np.array(mode_index_bend_radius_to_couplings[output_mode]) - tidy3d_results[f'coupling_0{output_mode}']) for output_mode in modes_to_compare_and_plot
    ])
    max_diff = np.max(np.abs(meow_tidy3d_diff))

    if visualize:
        import matplotlib.pyplot as plt
        _fig, ax = plt.subplots(layout='constrained', dpi=300)

        for output_mode, coupling_arr in mode_index_bend_radius_to_couplings.items():
            ax.plot(tidy3d_results.bend_radius,
                    tidy3d_results[f'coupling_0{output_mode}'],
                    label=f"Mode 0 -> {output_mode} coupling (Tidy3D)",
                    linestyle="dotted", linewidth=2)
            ax.plot(bend_radius_arr,
                    coupling_arr,
                    label=f"Mode 0 -> {output_mode} coupling (MEOW)",
                    linestyle="solid",
                    linewidth=0.5)
        ax.legend()
        ax.set_xlabel("Bend radius (um)")
        ax.set_ylabel("Coupling to output modes")
        ax.set_title(f"Coupling vs bend radius. Max difference: {max_diff:.5f}")
        plt.show()

    if max_diff > 0.01:
        error_msg = f"MEOW results do not closely match Tidy3D results. Max difference: {max_diff}"
        raise AssertionError(error_msg)

if __name__ == "__main__":
    # if run with command line argument -visualize, visualize results. Else, time all results
    import sys
    visualize = '-visualize' in sys.argv
    if visualize:
        test_evanescent_coupler_matches_tidy3d()
        test_mmi_matches_tidy3d()
        test_taper_matches_tidy3d()
        test_bend_matches_tidy3d()
    else:
        # time all tests individually
        import time
        start = time.time()
        test_evanescent_coupler_matches_tidy3d()
        print(f"test_evanescent_coupler_matches_tidy3d took {time.time() - start:.2f} seconds")

        start = time.time()
        test_mmi_matches_tidy3d()
        print(f"test_mmi_matches_tidy3d took {time.time() - start:.2f} seconds")

        start = time.time()
        test_taper_matches_tidy3d()
        print(f"test_taper_matches_tidy3d took {time.time() - start:.2f} seconds")

        start = time.time()
        test_bend_matches_tidy3d()
        print(f"test_bend_matches_tidy3d took {time.time() - start:.2f} seconds")