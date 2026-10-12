import numpy as np
import pandas as pd
from pathlib import Path

import meow as mw

def test_evanescent_coupler_matches_tidy3d(visualize: bool=False):
    # load tidy3d results
    tidy3d_results_fname = Path(__file__).resolve().parent / "assets" / "tidy3d_evanescent_coupler_data.csv"
    tidy3d_results = pd.read_csv(tidy3d_results_fname)

    # construct simulation that matches tidy3d example
    si = mw.TidyMaterial(name="cSi", variant="Li1993_293K")
    sio2 = mw.TidyMaterial(name="SiO2", variant="Palik_LowLoss")
    
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

    env = mw.Environment(T=20, wl=1.55)
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
        from matplotlib import pyplot as plt
        plt.plot(interaction_length_arr, coupling_00_arr, label="Coupling mode 0 -> 0 (MEOW)")
        plt.plot(tidy3d_results.length, tidy3d_results.coupling_00, label="Coupling mode 0 -> 0 (Tidy3D)", linestyle="dashed")
        plt.legend()
        plt.xlabel("Interaction length (um)")
        plt.ylabel("Coupling")
        plt.title("Coupling vs interaction length")
        plt.show()

    meow_tidy3d_diff = np.abs(np.array(coupling_00_arr) - tidy3d_results.coupling_00)

    if visualize:
        print(f"Max difference between MEOW and Tidy3D results: {np.max(np.abs(meow_tidy3d_diff))}")

    if np.max(np.abs(meow_tidy3d_diff)) > 0.02:
        raise AssertionError(f"MEOW results do not closely match Tidy3D results. Max difference: {np.max(np.abs(meow_tidy3d_diff))}")


if __name__ == "__main__":
    # If we're running this test from the command line, visualize results
    test_evanescent_coupler_matches_tidy3d(visualize=True)