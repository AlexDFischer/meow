import numpy as np
import pandas as pd
from pathlib import Path

import meow as mw

si = mw.TidyMaterial(name="cSi", variant="Li1993_293K")
sio2 = mw.TidyMaterial(name="SiO2", variant="Palik_LowLoss")
sin = mw.TidyMaterial(name="Si3N4", variant="Luke2015PMLStable")
env = mw.Environment(T=20, wl=1.55)

def test_evanescent_coupler_matches_tidy3d(visualize: bool=False):
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
        Ls=[1, 1, 1],
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_modes = [1, 2, 1]  # number of modes to compute for each cross-section
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    S_matrix, port_map = mw.compute_s_matrix(modes=modes,
                        cells=cells)

    interaction_length_arr = np.linspace(0, 50, 100)
    cell_lengths_arr = [[1, length, 1] for length in interaction_length_arr]
    coupling_00_arr = []

    for cell_lengths in cell_lengths_arr:
        S_matrix, port_map = mw.compute_s_matrix(modes=modes, cell_lengths=cell_lengths)
        coupling_00_arr.append(np.abs(S_matrix[0][1])**2)

    if visualize:
        import matplotlib
        from matplotlib import pyplot as plt

        fig, ax = plt.subplots(layout='constrained', dpi=300)

        ax.plot(tidy3d_results.length, tidy3d_results.coupling_00, label="Coupling (Tidy3D)", linestyle="dotted", linewidth=2)
        ax.plot(interaction_length_arr, coupling_00_arr, label="Coupling (MEOW)", linestyle="solid", linewidth=0.5)
        ax.legend()
        ax.set_xlabel("Interaction length (um)")
        ax.set_ylabel("Coupling")
        ax.set_title("Coupling vs interaction length")
        plt.show()

    meow_tidy3d_diff = np.abs(np.array(coupling_00_arr) - tidy3d_results.coupling_00)

    if visualize:
        print(f"Max difference between MEOW and Tidy3D results: {np.max(np.abs(meow_tidy3d_diff))}")

    if np.max(np.abs(meow_tidy3d_diff)) > 0.01:
        raise AssertionError(f"MEOW results do not closely match Tidy3D results. Max difference: {np.max(np.abs(meow_tidy3d_diff))}")

def test_mmi_matches_tidy3d(visualize: bool=False):
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_mmi_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example

    silicon_height = 0.22
    width_mmi = 8.0
    length_mmi = 57.5
    waveguide_width = 1.5
    cladding_buffer = 1.5
    output_waveguide_offset = 2.0
    dl = 0.010

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
        Ls=[1, length_mmi, 1],
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_mmi_modes = 15
    num_modes = [1, num_mmi_modes, 1]
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    if visualize:
        import matplotlib
        from matplotlib import pyplot as plt

        mw.visualize(modes[2][0], fields=['Ex'], operation=np.real)

        z_arr = np.linspace(0, length_mmi + 2, 1000)
        field, x = mw.propagate_modes(modes, cells, y=0, z=z_arr)

        fig, ax = plt.subplots(figsize=(10, 4))
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
        S_matrix, port_map = mw.compute_s_matrix(modes=modes, cell_lengths=[1, length, 1])
        output_coupling_symmetric_mode_arr.append(np.abs(S_matrix[0][1])**2)

    if visualize:
        fig, ax = plt.subplots(layout='constrained', dpi=300)

        ax.plot(tidy3d_results.length, tidy3d_results.coupling_00, label="Coupling (Tidy3D)", linestyle="dotted", linewidth=2)
        ax.plot(length_arr, output_coupling_symmetric_mode_arr, label="Coupling (MEOW)", linestyle="solid", linewidth=0.5)
        ax.legend()
        ax.set_xlabel("MMI length (um)")
        ax.set_ylabel("Coupling to symmetric output mode")
        ax.set_title("Coupling vs MMI length")
        plt.show()

    meow_tidy3d_diff = np.abs(np.array(output_coupling_symmetric_mode_arr) - tidy3d_results.coupling_00)

    if visualize:
        print(f"Max difference between MEOW and Tidy3D results: {np.max(np.abs(meow_tidy3d_diff))}")

    if np.max(np.abs(meow_tidy3d_diff)) > 0.01:
        raise AssertionError(f"MEOW results do not closely match Tidy3D results. Max difference: {np.max(np.abs(meow_tidy3d_diff))}")

def test_taper_matches_tidy3d(visualize: bool=False):
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_taper_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example

    silicon_height = 0.22
    waveguide_width_start = 0.45
    waveguide_width_end = 1.5
    taper_length = 20.0
    cladding_buffer = 1.5
    dl = 0.02

    x_min = -waveguide_width_end / 2 - cladding_buffer
    x_max = +waveguide_width_end / 2 + cladding_buffer
    y_min = -silicon_height / 2 - cladding_buffer
    y_max = +silicon_height / 2 + cladding_buffer

    num_cells = 30
    num_modes_per_cell = 9

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
        Ls=[taper_length / num_cells for _ in range(num_cells)],
        z_min=0,
    )

    xsecs = [mw.CrossSection.from_cell(cell=cell, env=env) for cell in cells]
    num_modes = [1]
    num_modes.extend([num_modes_per_cell] * (num_cells - 1))
    modes = [mw.compute_modes(cs=xsec, num_modes=num_modes[i]) for i, xsec in enumerate(xsecs)]

    modes_to_compare_and_plot = [0, 2, 4] # only plot even modes, as those are the only ones that should couple to the even fundamental mode that we excite

    if visualize:
        # visualize propagation
        import matplotlib
        from matplotlib import pyplot as plt

        z_arr = np.linspace(0, taper_length, 500)
        field, x = mw.propagate_modes(modes, cells, y=0, z=z_arr)

        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.pcolormesh(z_arr, x, np.abs(field).T, shading="auto", cmap="magma")
        ax.set_xlabel("z [um]")
        ax.set_ylabel("x [um]")
        ax.set_title("|Ex(x, z)| from mw.propagate_modes")
        plt.colorbar(im, ax=ax, label="|Ex|")
        plt.tight_layout()
        plt.show()

    output_mode_to_coupling_arr = {}

    for output_mode in modes_to_compare_and_plot:
        output_mode_to_coupling_arr[output_mode] = []

    length_arr = np.linspace(0, 10, 45)
    for length in length_arr:
        S_matrix, port_map = mw.compute_s_matrix(modes=modes, cell_lengths=[length / num_cells for _ in range(num_cells)])
        for output_mode in modes_to_compare_and_plot:
            output_mode_to_coupling_arr[output_mode].append(np.abs(S_matrix[0][1 + output_mode])**2)

    if visualize:
        fig, ax = plt.subplots(layout='constrained', dpi=300)

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
        ax.set_title("Coupling vs taper length")
        plt.show()

    meow_tidy3d_diff = np.max([
        np.abs(np.array(output_mode_to_coupling_arr[output_mode]) - tidy3d_results[f'coupling_0{output_mode}']) for output_mode in modes_to_compare_and_plot
    ])

    if visualize:
        print(f"Max difference between MEOW and Tidy3D results: {np.max(np.abs(meow_tidy3d_diff))}")

    if np.max(np.abs(meow_tidy3d_diff)) > 0.01:
        raise AssertionError(f"MEOW results do not closely match Tidy3D results. Max difference: {np.max(np.abs(meow_tidy3d_diff))}")

# def test_bend_matches_tidy3d(visualize: bool=False):
#     # load tidy3d results
#     # tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_bend_data.csv"
#     # tidy3d_results = pd.read_csv(tidy3d_results_fname)

#     max_bend_radius = 20

#     # structure is just a straight waveguide
#     # we manually modify the bend radius in each cell

#     waveguide_height = 0.5
#     waveguide_width = 1
#     waveguide_length = 30
#     cladding_buffer = 2.5
#     dl = 0.05

#     x_min = -waveguide_width / 2 - cladding_buffer
#     x_max = +waveguide_width / 2 + cladding_buffer
#     y_min = -waveguide_height / 2 - cladding_buffer
#     y_max = +waveguide_height / 2 + cladding_buffer

#     num_cells = 10
#     num_modes_per_cell = 9

#     waveguide = mw.Structure(
#         material=mw.silicon_nitride,
#         geometry=mw.Box(
#             x_min=-waveguide_width / 2,
#             x_max=+waveguide_width / 2,
#             y_min=-waveguide_height / 2,
#             y_max=+waveguide_height / 2,
#             z_min=0,
#             z_max=waveguide_length
#         ),
#         mesh_order=1
#     )
#     cladding = mw.Structure(
#         material=mw.silicon_oxide,
#         geometry=mw.Box(
#             x_min=-waveguide_width / 2 - cladding_buffer,
#             x_max=+waveguide_width / 2 + cladding_buffer,
#             y_min=-waveguide_height / 2 - cladding_buffer,
#             y_max=+waveguide_height / 2 + cladding_buffer,
#             z_min=0,
#             z_max=waveguide_length,
#         ),
#         mesh_order=2
#     )

#     if visualize:
#         import matplotlib
#         from matplotlib import pyplot as plt

#         fig, ax = plt.subplots(layout='constrained', dpi=300)

#         ax.plot(tidy3d_results.num_points, tidy3d_results.bend_loss, label="Bend loss (Tidy3D)", linestyle="dotted", linewidth=2)
#         ax.axhline(y=bend_loss, color='r', linestyle='--', label="Bend loss (MEOW)")
#         ax.legend()
#         ax.set_xlabel("Number of points in Euler curve (one greater than number of EME cells)")
#         ax.set_ylabel(f"Bend losses (dB)")
#         ax.set_title(f"Bend losses vs number of points in Euler curve for bend radius {bend_radius} um")
#         plt.show()

#     meow_tidy3d_diff = np.abs(bend_loss - tidy3d_results.bend_loss.iloc[-1])

#     if visualize:
#         print(f"Max difference between MEOW and Tidy3D results: {np.max(np.abs(meow_tidy3d_diff))}")

#     if np.max(np.abs(meow_tidy3d_diff)) > 0.01:
#         raise AssertionError(f"MEOW results do not closely match Tidy3D results. Max difference: {np.max(np.abs(meow_tidy3d_diff))}")

if __name__ == "__main__":
    # If we're running this test from the command line, visualize results
    # test_evanescent_coupler_matches_tidy3d(visualize=True)
    # test_mmi_matches_tidy3d(visualize=True)
    test_taper_matches_tidy3d(visualize=True)