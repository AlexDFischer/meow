"""Input validation for backends that export scalar structure materials."""

from meow.materials import (
    AnisotropicDispersiveMaterial,
    AnisotropicIndexMaterial,
    Material,
    SampledAnisotropicMaterial,
    SpatiallyVaryingMaterial,
    TidyMaterial,
    UniaxialDispersiveMaterial,
    VariantItemUniaxial,
    material_library,
)
from meow.mesh import Mesh2D


def reject_adiabatic_absorbers(mesh: Mesh2D, backend: str) -> None:
    """Reject an absorber profile that the backend would otherwise ignore."""
    if any(
        (
            mesh._absorber_left,
            mesh._absorber_right,
            mesh._absorber_top,
            mesh._absorber_bottom,
        )
    ):
        msg = f"The {backend} backend does not support adiabatic absorbers."
        raise NotImplementedError(msg)


def require_uniform_isotropic_material(material: Material, backend: str) -> None:
    """Reject materials that cannot be exported as one scalar per structure."""
    if isinstance(material, SpatiallyVaryingMaterial):
        msg = (
            f"The {backend} backend does not support "
            f"spatially varying material {material.name!r}."
        )
        raise NotImplementedError(msg)

    anisotropic = isinstance(
        material,
        (
            AnisotropicIndexMaterial,
            SampledAnisotropicMaterial,
            AnisotropicDispersiveMaterial,
            UniaxialDispersiveMaterial,
        ),
    )
    if isinstance(material, TidyMaterial):
        variant = material_library[material.name].variants[material.variant]
        anisotropic = isinstance(variant, VariantItemUniaxial)
    if anisotropic:
        msg = (
            f"The {backend} backend does not support "
            f"anisotropic material {material.name!r}."
        )
        raise NotImplementedError(msg)
