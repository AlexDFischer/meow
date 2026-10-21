import pytest

def test_nonincreasing_mesh_fails():
    from meow.mesh import Mesh2D
    import numpy as np

    with pytest.raises(ValueError, match="x coordinates must be strictly increasing"):
        Mesh2D(x=np.array([0, 1, 1]), y=np.array([0, 1, 2]))

    with pytest.raises(ValueError, match="x coordinates must be strictly increasing"):
        Mesh2D(x=np.array([0, 1, 0.9]), y=np.array([0, 1, 2]))

    with pytest.raises(ValueError, match="y coordinates must be strictly increasing"):
        Mesh2D(x=np.array([0, 1, 2]), y=np.array([0, 1, 1]))

    with pytest.raises(ValueError, match="y coordinates must be strictly increasing"):
        Mesh2D(x=np.array([0, 1, 2]), y=np.array([0, 1, 2, 1.8, 3, 4]))

    # Also make a good (x and y increasing) meshes and make sure there are no exceptions
    Mesh2D(x=np.array([0, 1, 2, 3]), y=np.array([4, 5, 6, 7]))