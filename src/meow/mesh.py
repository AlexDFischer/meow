"""A 2D Mesh."""

from __future__ import annotations

from typing import Annotated, Any, Literal

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle as MplRect
from pydantic import BeforeValidator, Field, PrivateAttr
from pydantic.types import NonNegativeInt

from meow.arrays import FloatArray1D, FloatArray2D
from meow.base_model import BaseModel, cached_property

PML_DEFAULT_RGBA = (0.3, 0.3, 0.3, 0.4)
ABSORBER_DEFAULT_RGBA = (0.6, 0.6, 0.6, 0.4)


class AbsorberParams(BaseModel):
    """Parameters that define absorbing boundary.

    The parameters describe how slowly Im[neff] ramps up towards the edge. These are
    separate from PMLs, and are best used when something prevents PMLs form working,
    such as non-uniform structures extending into the boundary (eg photonic crystals).
    """

    length: float = Field(
        description="Length in um of absorber", gt=0, allow_inf_nan=False
    )

    end_extinction_coef: float = Field(
        description="Imaginary part that gets added to refractive index at end of \
            absorber",
        default=1.0,
    )

    transition_power: float = Field(
        description="Polynomial degree of transition to higher extinction \
            coefficient. Default 3.",
        default=3,
    )

    def extinction_coef(self, distance_from_edge: FloatArray2D) -> FloatArray2D:
        """Extinction coefficient (Im[n]) as function of distance from edge.

        Args:
            distance_from_edge (FloatArray2D): distance from outer boundary of
            simulation on this side.

        Returns:
            FloatArray2D: Extinction coefficient (Im[n]) at the given distances from
            the edge.
        """
        return np.select(
            [distance_from_edge < self.length],
            [
                self.end_extinction_coef
                * ((self.length - distance_from_edge) / self.length)
                ** self.transition_power
            ],
            default=0,
        )


class Mesh2D(BaseModel):
    """A ``Mesh2D`` describes how a ``Structure3D`` is discritized into a ``Cell``."""

    x: FloatArray1D = Field(
        description="x-coords of the mesh (Ez locations, i.e. corners of the 2D cell)"
    )

    y: FloatArray1D = Field(
        description="y-coords of the mesh (Ez locations, i.e. corners of the 2D cell)"
    )

    angle_phi: float = Field(
        default=0.0,
        description=(
            "Azimuth angle of the propagation axis in the plane orthogonal to the mesh."
        ),
    )
    angle_theta: float = Field(
        default=0.0,
        description="Polar angle of the propagation axis from the injection axis.",
    )
    bend_radius: Annotated[
        float, BeforeValidator(lambda x: np.nan if x is None else x)
    ] = Field(
        default=np.nan,
        description=(
            "A curvature radius for simulation of waveguide bends. Can be negative, "
            "in which case the mode plane center has a smaller value than the "
            "curvature center along the tangential axis perpendicular to the bend axis."
        ),
    )
    bend_axis: Literal[0, 1] = Field(
        default=0,
        description=(
            "Index into the two tangential axes defining the normal to the plane in "
            "which the bend lies. This must be provided if ``bend_radius`` is not "
            "``None``. For example, for a ring in the global xy-plane, and a mode "
            "plane in either the xz or the yz plane, the ``bend_axis`` is always 1 "
            "(the global z axis)."
        ),
    )
    plane_center: tuple[float, float] = Field(
        default=(0.0, 0.0),
        description=(
            "If ``bend_radius`` is not ``None``, the position of the plane "
            "corresponding along the circonference of the circle"
        ),
    )

    num_pml: tuple[NonNegativeInt, NonNegativeInt] = Field(
        default=(0, 0),
        description="Number of standard pml layers to add in the two tangential axes.",
    )

    absorbing_boundary: AbsorberParams | None = None
    absorbing_boundary_x: AbsorberParams | None = None
    absorbing_boundary_y: AbsorberParams | None = None
    absorbing_boundary_left: AbsorberParams | None = None
    absorbing_boundary_right: AbsorberParams | None = None
    absorbing_boundary_top: AbsorberParams | None = None
    absorbing_boundary_bottom: AbsorberParams | None = None

    # internal attributes that store the absorber for each side, determined from above
    # options
    _absorber_left: AbsorberParams | None = PrivateAttr(default=None)
    _absorber_right: AbsorberParams | None = PrivateAttr(default=None)
    _absorber_top: AbsorberParams | None = PrivateAttr(default=None)
    _absorber_bottom: AbsorberParams | None = PrivateAttr(default=None)

    def model_post_init(self, context: Any) -> None:
        """Validate coordinates and resolve a single absorber per side."""
        super().model_post_init(context)

        x_diff = self.x[1:] - self.x[:-1]
        if (x_diff <= 0).any():
            msg = "x coordinates must be strictly increasing"
            raise ValueError(msg)

        y_diff = self.y[1:] - self.y[:-1]
        if (y_diff <= 0).any():
            msg = "y coordinates must be strictly increasing"
            raise ValueError(msg)

        all_sides = self.absorbing_boundary
        x_sides = self.absorbing_boundary_x
        y_sides = self.absorbing_boundary_y
        left = self.absorbing_boundary_left
        right = self.absorbing_boundary_right
        top = self.absorbing_boundary_top
        bottom = self.absorbing_boundary_bottom

        if all_sides is not None and any(
            absorber is not None
            for absorber in (x_sides, y_sides, left, right, top, bottom)
        ):
            msg = "absorbing_boundary cannot be combined with axis or side absorbers"
            raise ValueError(msg)

        if x_sides is not None and (left is not None or right is not None):
            msg = (
                "absorbing_boundary_x cannot be combined with "
                "absorbing_boundary_left or absorbing_boundary_right"
            )
            raise ValueError(msg)

        if y_sides is not None and (top is not None or bottom is not None):
            msg = (
                "absorbing_boundary_y cannot be combined with "
                "absorbing_boundary_top or absorbing_boundary_bottom"
            )
            raise ValueError(msg)

        self._absorber_left = left or x_sides or all_sides
        self._absorber_right = right or x_sides or all_sides
        self._absorber_top = top or y_sides or all_sides
        self._absorber_bottom = bottom or y_sides or all_sides

        for coords, sides, absorbers in (
            (self.x, "left and right", (self._absorber_left, self._absorber_right)),
            (self.y, "top and bottom", (self._absorber_top, self._absorber_bottom)),
        ):
            span = coords[-1] - coords[0] if coords.size else 0.0
            total_length = sum(
                absorber.length for absorber in absorbers if absorber is not None
            )
            if total_length > span:
                msg = f"{sides} boundary absorbers overlap or exceed the mesh span"
                raise ValueError(msg)

    @cached_property
    def dx(self) -> FloatArray1D:
        """dx at Hz locations, i.e. center of the 2D cell."""
        return self.x[1:] - self.x[:-1]

    @cached_property
    def dy(self) -> FloatArray1D:
        """dy at Hz locations, i.e. center of the 2D cell."""
        return self.y[1:] - self.y[:-1]

    @cached_property
    def x_(self) -> FloatArray1D:
        """x at Hz locations, i.e. center of the 2D cell."""
        return 0.5 * (self.x[1:] + self.x[:-1])

    @cached_property
    def y_(self) -> FloatArray1D:
        """y at Hz locations, i.e. center of the 2D cell."""
        return 0.5 * (self.y[1:] + self.y[:-1])

    @cached_property
    def x_full(self) -> FloatArray1D:
        """x at half-integer locations."""
        return np.stack([self.x[:-1], self.x[:-1] + self.dx / 2], 1).ravel()

    @cached_property
    def y_full(self) -> FloatArray1D:
        """y at half-integer locations."""
        return np.stack([self.y[:-1], self.y[:-1] + self.dy / 2], 1).ravel()

    @cached_property
    def XY_full(self) -> tuple[FloatArray2D, FloatArray2D]:
        """X and Y at half-integer locations."""
        Y_full, X_full = np.meshgrid(self.y_full, self.x_full)
        return X_full, Y_full

    @property
    def X_full(self) -> FloatArray2D:
        """X at half-integer locations."""
        return self.XY_full[0]

    @property
    def Y_full(self) -> FloatArray2D:
        """Y at half-integer locations."""
        return self.XY_full[1]

    @property
    def Xx(self) -> FloatArray2D:
        """X at Ex locations."""
        return self.X_full[1::2, ::2]

    @property
    def Yx(self) -> FloatArray2D:
        """Y at Ex locations."""
        return self.Y_full[1::2, ::2]

    @property
    def Xy(self) -> FloatArray2D:
        """X at Ey locations."""
        return self.X_full[::2, 1::2]

    @property
    def Yy(self) -> FloatArray2D:
        """Y at Ey locations."""
        return self.Y_full[::2, 1::2]

    @property
    def Xz(self) -> FloatArray2D:
        """X at Ez locations."""
        return self.X_full[::2, ::2]

    @property
    def Yz(self) -> FloatArray2D:
        """Y at Ez locations."""
        return self.Y_full[::2, ::2]

    @property
    def Xz_(self) -> FloatArray2D:
        """X at Hz locations."""
        return self.X_full[1::2, 1::2]

    @property
    def Yz_(self) -> FloatArray2D:
        """Y at Hz locations."""
        return self.Y_full[1::2, 1::2]


def _pml_boxes(mesh: Mesh2D) -> list[tuple[float, float, float, float]]:
    """Get the bounding boxes of the PML regions of a ``Mesh2D``.

    Args:
        mesh: the mesh whose PML regions to compute.

    Returns:
        A list of ``(x_min, x_max, y_min, y_max)`` tuples, one per PML region.
        The corner regions are not listed separately, as they are already
        covered by the x- and y-bands. Returns an empty list if the mesh has no
        PML layers.
    """
    numx, numy = mesh.num_pml
    if numx == 0 and numy == 0:
        return []

    x_min = mesh.x[0]
    x_max = mesh.x_[-1]
    y_min = mesh.y[0]
    y_max = mesh.y_[-1]

    boxes = []
    x_lo = x_min
    x_hi = x_max
    if numx > 0:
        # full height: this also covers the four corner regions
        x_lo = mesh.x[numx]
        x_hi = mesh.x[-1 - numx]
        boxes.append((x_min, x_lo, y_min, y_max))
        boxes.append((x_hi, x_max, y_min, y_max))
    if numy > 0:
        # between the x-bands, such that corners are not drawn twice
        y_lo = mesh.y[numy]
        y_hi = mesh.y[-1 - numy]
        boxes.append((x_lo, x_hi, y_min, y_lo))
        boxes.append((x_lo, x_hi, y_hi, y_max))

    return boxes


def _draw_pml(
    ax: Axes,
    mesh: Mesh2D,
    color: tuple[float, float, float, float] = PML_DEFAULT_RGBA,
    zorder: float = 2,
) -> list[MplRect]:
    """Draw the PML regions of a mesh as grey rectangles on the given axes.

    Intended to be drawn on top of an existing mode or cross-section plot
    (whose axes are in the same coordinates as ``mesh``), such that the PML
    regions used by the simulation are clearly indicated.

    Args:
        ax: the matplotlib axes to draw on.
        mesh: the mesh whose PML regions to draw. Its ``x`` and ``y`` cell-edge
            coordinates define the extents of the drawn rectangles.
        color: the RGB color of the PML rectangles. Defaults to a mid grey.
        alpha: the opacity of the PML rectangles. Defaults to 0.5.
        zorder: the matplotlib z-order to draw the rectangles at. Defaults to 2,
            which is below the mode image drawn by ``Mode._visualize``.

    Returns:
        The list of added ``matplotlib.patches.Rectangle`` patches.
    """
    patches = []
    for x0, x1, y0, y1 in _pml_boxes(mesh):
        if x1 <= x0 or y1 <= y0:
            continue
        rect = MplRect(
            (x0, y0),
            x1 - x0,
            y1 - y0,
            facecolor=color[:3],
            edgecolor="none",
            alpha=color[3],
            zorder=zorder,
        )
        ax.add_patch(rect)
        patches.append(rect)

    return patches


def _draw_mesh(
    ax: Axes,
    mesh: Mesh2D,
    option: str = "primal",
    **line_kwargs: Any,
) -> None:
    """Plot the mesh.

    Args:
        ax (matplotlib.axes.Axes): `Axes` object to plot mesh on. Typically you will
        plot on top of an already drawn `Cell` or `CrossSection`.
        mesh (Mesh2D): mesh to draw.
        option (str, optional): which mesh to draw. Options are 'primal', which means
        the x and y passed to `Mesh2D()` that is where Ez is on the Yee grid; 'dual',
        which is half way between points on the primal grid and is where Hz is on the
        Yee grid, and 'full', which draws both grids. Defaults to 'primal'.
        line_kwargs: additional keyword arguments passed to `ax.axvline` and
        `ax.axhline` for styling the mesh lines.

    """
    line_kwargs.setdefault("linewidth", 0.5)
    line_kwargs.setdefault("color", "black")

    if option == "primal":
        for x in mesh.x:
            ax.axvline(x, **line_kwargs)
        for y in mesh.y:
            ax.axhline(y, **line_kwargs)
    elif option == "dual":
        for x in mesh.x_:
            ax.axvline(x, **line_kwargs)
        for y in mesh.y_:
            ax.axhline(y, **line_kwargs)
    elif option == "full":
        for x in mesh.x_full:
            ax.axvline(x, **line_kwargs)
        for y in mesh.y_full:
            ax.axhline(y, **line_kwargs)
    else:
        msg = f"option must be 'primal', 'dual', or 'full', but got {option!r}"
        raise ValueError(msg)
