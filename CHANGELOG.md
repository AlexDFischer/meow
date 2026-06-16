<a id="0.15.0"></a>
# [0.15.0](https://github.com/gdsfactory/meow/releases/tag/0.15.0) - 2026-03-15

## Bug Fixes

- Fix top PML energy slice in is_pml_mode [#53](https://github.com/gdsfactory/meow/pull/53)
- fix eme r2l lossy projection [#52](https://github.com/gdsfactory/meow/pull/52)

## Documentation

- Big refactoring [#54](https://github.com/gdsfactory/meow/pull/54)

<a id="0.14.1"></a>
# [0.14.1](https://github.com/gdsfactory/meow/releases/tag/0.14.1) - 2025-06-23

## Dependency Updates

- bump sax [#50](https://github.com/gdsfactory/meow/pull/50)

<a id="0.14.0"></a>
# [0.14.0](https://github.com/gdsfactory/meow/releases/tag/0.14.0) - 2025-06-20

## New

- Bump sax + ruff + pyright refactoring [#49](https://github.com/gdsfactory/meow/pull/49)

## Other changes

- Definition of plane_center for bend mode solving [#48](https://github.com/gdsfactory/meow/pull/48)
- Implementation of Polygon2D variant for Geometry2D [#47](https://github.com/gdsfactory/meow/pull/47)
- Change logo [#46](https://github.com/gdsfactory/meow/pull/46)

<a id="0.13.0"></a>
# [0.13.0](https://github.com/gdsfactory/meow/releases/tag/0.13.0) - 2025-04-13

## New

- Add precision

## Bug Fixes

- Fix deps
- Fix notebook

## Documentation

- Update docs Makefile

## Dependency Updates

- Update bumpversion config
- Merge pull request [#45](https://github.com/gdsfactory/meow/issues/45) from joamatab/update_tidy3d
- Update tidyed
- Update github workflows
- Update dependencies
- Update github workflows
- Update github ci

<a id="0.12.0"></a>
# [0.12.0](https://github.com/gdsfactory/meow/releases/tag/0.12.0) - 2025-02-13

## New

- Merge pull request [#42](https://github.com/gdsfactory/meow/issues/42) from flaport/40-documentation-suggestions
- DOC: Documentation additions + nbstripout

## Dependency Updates

- Update dependencies
- Merge pull request [#43](https://github.com/gdsfactory/meow/issues/43) from joamatab/numpy2_compat
- Update to numpy2

<a id="0.11.2"></a>
# [0.11.2](https://github.com/gdsfactory/meow/releases/tag/0.11.2) - 2024-08-06

## Bug Fixes

- Merge pull request [#38](https://github.com/gdsfactory/meow/issues/38) from joamatab/patch-1
- Merge branch 'main' into patch-1

<a id="0.11.1"></a>
# [0.11.1](https://github.com/gdsfactory/meow/releases/tag/0.11.1) - 2024-08-04

## Dependency Updates

- Update gds_structures.py
- Update requirements

## Other changes

- Better equality check
- Don't use Self for now

<a id="0.11.0"></a>
# [0.11.0](https://github.com/gdsfactory/meow/releases/tag/0.11.0) - 2024-06-20

## New

- Merge pull request [#36](https://github.com/gdsfactory/meow/issues/36) from flaport/pydantic-v2

## Bug Fixes

- Fix tests

## Documentation

- Update docs

## Maintenance

- Improve serialization and caching

## Other changes

- Exclusively support pydantic v2

<a id="0.10.0"></a>
# [0.10.0](https://github.com/gdsfactory/meow/releases/tag/0.10.0) - 2024-06-15

## Bug Fixes

- Fix tests
- Fix notebook

## Other changes

- Works for gdsfactory8

<a id="0.9.0"></a>
# [0.9.0](https://github.com/gdsfactory/meow/releases/tag/0.9.0) - 2024-01-19

## New

- Adopt new sax backend format

## Bug Fixes

- Merge pull request [#34](https://github.com/gdsfactory/meow/issues/34) from flaport/sax0.11-compatibility
- Fix by manually converting to scoo

## Dependency Updates

- Pin sax

<a id="0.8.1"></a>
# [0.8.1](https://github.com/gdsfactory/meow/releases/tag/0.8.1) - 2023-09-19

## Dependency Updates

- Bump tidy3d

<a id="0.8.0"></a>
# [0.8.0](https://github.com/gdsfactory/meow/releases/tag/0.8.0) - 2023-09-05

## Dependency Updates

- Bump sax dependency

<a id="0.7.3"></a>
# [0.7.3](https://github.com/gdsfactory/meow/releases/tag/0.7.3) - 2023-08-30

## Bug Fixes

- Fix notebooks

## Dependency Updates

- Update dependencies
- Bump pydantic to v2 using pydantic.v1

<a id="0.7.2"></a>
# [0.7.2](https://github.com/gdsfactory/meow/releases/tag/0.7.2) - 2023-08-04

## Dependency Updates

- Merge pull request [#31](https://github.com/gdsfactory/meow/issues/31) from joamatab/pin_pydantic
- Pin pydantic

<a id="0.7.1"></a>
# [0.7.1](https://github.com/gdsfactory/meow/releases/tag/0.7.1) - 2023-07-09

## Other changes

- Explicit imports of objects in __init__

<a id="0.7.0"></a>
# [0.7.0](https://github.com/gdsfactory/meow/releases/tag/0.7.0) - 2023-07-06

## New

- Add Structure utility function which creates either a Structure2D or a Structure3D depending on the geometry given
- Add 2D geometries

## Bug Fixes

- Fix remaining tests
- Fix notebooks
- Fix syntax error
- Merge pull request [#27](https://github.com/gdsfactory/meow/issues/27) from flaport/te_fraction_patch
- Patch problem with complex index in `te_fraction`

## Documentation

- Update cell docstring
- Update mmi test notebook
- Make test notebooks runnable

## Dependency Updates

- Update .gitignore
- Update tidy3d.py to ignore eps spec

## Maintenance

- Minor refactoring on calculating material array
- Improve cell to be able to handle 2D structures

## Other changes

- Make propagation work with decoupled cross-sections
- Make lumerical fde work
- Make eme work for decoupled cross-sections
- Move ez_interfaces setting to mesh settings
- Sort final eme result ports
- Structure -> Structure3D, Structure2D
- Deprecate Mesh2d in favor of Mesh2D
- Remove unused line

<a id="0.6.9"></a>
# [0.6.9](https://github.com/gdsfactory/meow/releases/tag/0.6.9) - 2023-06-26

## New

- Add ez_boundaries option to create_cells function

## Dependency Updates

- Update meshing comparison

<a id="0.6.8"></a>
# [0.6.8](https://github.com/gdsfactory/meow/releases/tag/0.6.8) - 2023-06-23

## Bug Fixes

- Fix Pointing field plot

## Maintenance

- Improve ez boundaries by including them into Cell in stead of CrossSection

<a id="0.6.7"></a>
# [0.6.7](https://github.com/gdsfactory/meow/releases/tag/0.6.7) - 2023-06-22

<a id="0.6.6"></a>
# [0.6.6](https://github.com/gdsfactory/meow/releases/tag/0.6.6) - 2023-06-22

## Bug Fixes

- Fix some meshing issues and normalize modes properly

<a id="0.6.5"></a>
# [0.6.5](https://github.com/gdsfactory/meow/releases/tag/0.6.5) - 2023-06-19

## Bug Fixes

- Fix material serialization/deserialization

<a id="0.6.4"></a>
# [0.6.4](https://github.com/gdsfactory/meow/releases/tag/0.6.4) - 2023-06-19

## New

- Add edge case for better meshing
- Merge pull request [#22](https://github.com/gdsfactory/meow/issues/22) from flaport/materials
- Add support for tidy3d materials
- Add support for tidy3d materials

## Bug Fixes

- Merge pull request [#21](https://github.com/gdsfactory/meow/issues/21) from flaport/fix-typing
- Merge fix-typing into propagation

## Maintenance

- Make type checker happy

## Other changes

- Tolerance to klu not being present
- Use `Optional` instead of `|` to maintain compatibility to python<3.10

<a id="0.6.3"></a>
# [0.6.3](https://github.com/gdsfactory/meow/releases/tag/0.6.3) - 2023-06-18

## New

- Add field interpolation
- Add lumerical dielectric interfaces

<a id="0.6.2"></a>
# [0.6.2](https://github.com/gdsfactory/meow/releases/tag/0.6.2) - 2023-06-18

## Other changes

- Proper mesh locations

<a id="0.6.1"></a>
# [0.6.1](https://github.com/gdsfactory/meow/releases/tag/0.6.1) - 2023-06-17

## New

- Better meshing implementation

## Bug Fixes

- Fix lumerical field extraction

## Documentation

- Updates to better meshing notebook
- Update test notebook
- Format notebooks with black

## Dependency Updates

- Update parameter naming for PML filtering
- Update .gitignore

## Other changes

- Minor visualization tweaks
- Allow forcing Ez on dielectric boundaries

<a id="0.6.0"></a>
# [0.6.0](https://github.com/gdsfactory/meow/releases/tag/0.6.0) - 2023-06-15

## New

- Add cached_property

## Documentation

- Minor updates to notebooks

## Maintenance

- Minor cleanup of Material internals

<a id="0.5.6"></a>
# [0.5.6](https://github.com/gdsfactory/meow/releases/tag/0.5.6) - 2023-06-13

## Bug Fixes

- Temporary fix for mutiplication and division

## Other changes

- Allow specifying plot width to visualize modes
- Reject pml modes when using meow

<a id="0.5.5"></a>
# [0.5.5](https://github.com/gdsfactory/meow/releases/tag/0.5.5) - 2023-06-09

## Other changes

- Allow overriding cell length when calculating s-matrix

<a id="0.5.4"></a>
# [0.5.4](https://github.com/gdsfactory/meow/releases/tag/0.5.4) - 2023-06-09

## New

- Add pml filtering function

<a id="0.5.3"></a>
# [0.5.3](https://github.com/gdsfactory/meow/releases/tag/0.5.3) - 2023-06-09

## Bug Fixes

- Make it possible to patch in custom visualization functions into mw.visualize/mw.vis
- Attempt to fix github workflows

<a id="0.5.2"></a>
# [0.5.2](https://github.com/gdsfactory/meow/releases/tag/0.5.2) - 2023-06-08

## Bug Fixes

- Attempt to fix github workflows
- Add title_prefix argument to mode visualization function

## Documentation

- Update README

## Other changes

- Allow phase keyword for S, pm visualization

<a id="0.5.1"></a>
# [0.5.1](https://github.com/gdsfactory/meow/releases/tag/0.5.1) - 2023-06-07

## Maintenance

- Improve visualization functions

<a id="0.5.0"></a>
# [0.5.0](https://github.com/gdsfactory/meow/releases/tag/0.5.0) - 2023-06-07

## Bug Fixes

- Conjugate the nontransposed lr/rl matrix.

## Other changes

- Ensure reciprocity should not involve a hermitian transpose
- Don't take real part when using unconjugated

<a id="0.4.3"></a>
# [0.4.3](https://github.com/gdsfactory/meow/releases/tag/0.4.3) - 2023-06-06

## Other changes

- Increase json serialization accuracy

<a id="0.4.2"></a>
# [0.4.2](https://github.com/gdsfactory/meow/releases/tag/0.4.2) - 2023-06-06

## Other changes

- Minor rewrite of compute_modes

<a id="0.4.1"></a>
# [0.4.1](https://github.com/gdsfactory/meow/releases/tag/0.4.1) - 2023-06-05

## Other changes

- Default to double precision for tidy3d fde

<a id="0.4.0"></a>
# [0.4.0](https://github.com/gdsfactory/meow/releases/tag/0.4.0) - 2023-06-05

## Maintenance

- Better auto formatting

## Other changes

- Allow setting bend_radius to None

<a id="0.3.11"></a>
# [0.3.11](https://github.com/gdsfactory/meow/releases/tag/0.3.11) - 2023-06-05

## Other changes

- Ignore UserWarnings when plotting mode contours

<a id="0.3.10"></a>
# [0.3.10](https://github.com/gdsfactory/meow/releases/tag/0.3.10) - 2023-06-05

## Other changes

- Ignore RuntimeWarnings when doing shapely intersections

<a id="0.3.9"></a>
# [0.3.9](https://github.com/gdsfactory/meow/releases/tag/0.3.9) - 2023-06-05

## Other changes

- Fall back on gdspy if shapely has difficulties extruding polygon
- Mmi

<a id="0.3.8"></a>
# [0.3.8](https://github.com/gdsfactory/meow/releases/tag/0.3.8) - 2023-06-05

## Bug Fixes

- Fix some typing issues

<a id="0.3.7"></a>
# [0.3.7](https://github.com/gdsfactory/meow/releases/tag/0.3.7) - 2023-06-05

## Bug Fixes

- Fix imports and revert zero_phase function

<a id="0.3.6"></a>
# [0.3.6](https://github.com/gdsfactory/meow/releases/tag/0.3.6) - 2023-06-05

## New

- Add visualization for multiple modes
- Add function to create lumerical geometries

## Bug Fixes

- Fix matrix splitting
- Fix publish workflow
- Fix github workflows
- Merge pull request [#16](https://github.com/gdsfactory/meow/issues/16) from Jan-David-Black/main

## Documentation

- Move propagate guts out of notebook
- Update docs
- Update docs

## Other changes

- Propagate eme flags everywhere and set default values globally
- Allow both inner products, default to conjugate transpose version
- Make some changes to overlap calculation. Validation still pending
- Slightly better visualization
- Allow pml with lumerical fde
- With pre-commit hooks:
- Visual propagation result
- First propagation attempts
- L2r and r2l matrices
- Avoid phase dependence in interfaces
- Just use condaforge/mambaforge container for workflows
- Just use condaforge/mambaforge container for workflows
- Correct Typo `i->j`

<a id="0.3.5"></a>
# [0.3.5](https://github.com/gdsfactory/meow/releases/tag/0.3.5) - 2023-06-01

## Other changes

- Make eme work with unequal number of modes in each slice
- Allow interface matrix calc for diff num of modes
- Convenience functions for Mode arithmetics

<a id="0.3.4"></a>
# [0.3.4](https://github.com/gdsfactory/meow/releases/tag/0.3.4) - 2023-05-24

## New

- Add packaging dependency

## Bug Fixes

- Merge pull request [#11](https://github.com/gdsfactory/meow/issues/11) from Jan-David-Black/main

## Other changes

- Misspelled version
- Check tidy3d Version
- Fill in zero valued off-diagonal epsilon

<a id="0.3.3"></a>
# [0.3.3](https://github.com/gdsfactory/meow/releases/tag/0.3.3) - 2023-05-24

## Maintenance

- Improve extrusions

<a id="0.3.2"></a>
# [0.3.2](https://github.com/gdsfactory/meow/releases/tag/0.3.2) - 2023-05-23

## Maintenance

- Slightly clean up compute_s_matrix_sax

<a id="0.3.1"></a>
# [0.3.1](https://github.com/gdsfactory/meow/releases/tag/0.3.1) - 2023-05-23

## Other changes

- Propagations should not take absolute value

<a id="0.3.0"></a>
# [0.3.0](https://github.com/gdsfactory/meow/releases/tag/0.3.0) - 2023-05-18

## Bug Fixes

- Fix checks in meow.fde.lumerical

## Dependency Updates

- Make matplotlib and trimesh kind-off optional dependencies

<a id="0.2.0"></a>
# [0.2.0](https://github.com/gdsfactory/meow/releases/tag/0.2.0) - 2023-04-24

## Dependency Updates

- Clean up dependencies

<a id="0.1.5"></a>
# [0.1.5](https://github.com/gdsfactory/meow/releases/tag/0.1.5) - 2023-04-04

## Dependency Updates

- Pin tidy3d to version > 2

<a id="0.1.4"></a>
# [0.1.4](https://github.com/gdsfactory/meow/releases/tag/0.1.4) - 2023-04-04

## New

- Merge pull request [#8](https://github.com/gdsfactory/meow/issues/8) from Jan-David-Black/6
- Add mode area calculation (and integration util)
- Add taper length sweep example

## Bug Fixes

- Eme: workaround for bug in sax multimode
- Fix dependencies and tests
- Fix cache deletion for threaded applications
- Fix array hash

## Dependency Updates

- Merge pull request [#5](https://github.com/gdsfactory/meow/issues/5) from joamatab/remove_gdspy_dep
- Remove gdspy dependency

## Other changes

- Include Poynting Vector calculation
- Switch from tidy3d-beta to tidy3d

<a id="0.1.3"></a>
# [0.1.3](https://github.com/gdsfactory/meow/releases/tag/0.1.3) - 2022-11-30

## Bug Fixes

- Fix complex number deserialization

<a id="0.1.2"></a>
# [0.1.2](https://github.com/gdsfactory/meow/releases/tag/0.1.2) - 2022-11-23

## Other changes

- Don't sort modes by default
- Enable cache by default

<a id="0.1.1"></a>
# [0.1.1](https://github.com/gdsfactory/meow/releases/tag/0.1.1) - 2022-11-23

## New

- Introduce a cache

## Other changes

- Disable cache by default

<a id="0.1.0"></a>
# [0.1.0](https://github.com/gdsfactory/meow/releases/tag/0.1.0) - 2022-11-19

## Other changes

- Specify conformal settings as part of mesh settings

<a id="0.0.10"></a>
# [0.0.10](https://github.com/gdsfactory/meow/releases/tag/0.0.10) - 2022-11-18

## Maintenance

- Improve serialization again

<a id="0.0.9"></a>
# [0.0.9](https://github.com/gdsfactory/meow/releases/tag/0.0.9) - 2022-11-17

## Bug Fixes

- Fix float format

## Other changes

- Keep derived variables truly hidden

<a id="0.0.8"></a>
# [0.0.8](https://github.com/gdsfactory/meow/releases/tag/0.0.8) - 2022-11-17

## Other changes

- Ensure models have json schema

<a id="0.0.7"></a>
# [0.0.7](https://github.com/gdsfactory/meow/releases/tag/0.0.7) - 2022-11-15

## Bug Fixes

- Fix multi-dimensional material parsing

<a id="0.0.6"></a>
# [0.0.6](https://github.com/gdsfactory/meow/releases/tag/0.0.6) - 2022-11-13

## Dependency Updates

- Update requirements

<a id="0.0.5"></a>
# [0.0.5](https://github.com/gdsfactory/meow/releases/tag/0.0.5) - 2022-11-11

## Other changes

- Remove weird list-inheritance
- Don't track nbs_fail folder
- Use correct version of myst_nb

<a id="0.0.4"></a>
# [0.0.4](https://github.com/gdsfactory/meow/releases/tag/0.0.4) - 2022-11-11

## Bug Fixes

- Fix material parsing

## Documentation

- Improve pydantic docs

## Dependency Updates

- Update conda environment file

## Other changes

- Make te-fraction an easy to access property of a mode.

<a id="0.0.3"></a>
# [0.0.3](https://github.com/gdsfactory/meow/releases/tag/0.0.3) - 2022-11-10

## Documentation

- Improve docs

## Other changes

- More explicit backends
- Use latest tidy3d version
- Use latest sax version

<a id="0.0.2"></a>
# [0.0.2](https://github.com/gdsfactory/meow/releases/tag/0.0.2) - 2022-11-10

## New

- Add notebook integration tests

## Bug Fixes

- Fix serialization/deserialization
- Fix broken links in intro notebook
- Fix pypi upload

## Documentation

- Update readme

<a id="0.0.1"></a>
# [0.0.1](https://github.com/gdsfactory/meow/releases/tag/0.0.1) - 2022-11-09

## New

- Add publish logic
- Add mapbox-earcut dependency ([#2](https://github.com/gdsfactory/meow/issues/2))
- .gitignore added

## Bug Fixes

- Fix docs patches
- Fix .bumpversion config
- Docs: fix binder/colab links

## Documentation

- Update readme
- Build docs in ci

## Maintenance

- Merge pull request [#1](https://github.com/gdsfactory/meow/issues/1) from joamatab/sourcery/main
- 'Refactored by Sourcery'

## Other changes

- Remove wrong import
- Meow

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.9.1 -->
