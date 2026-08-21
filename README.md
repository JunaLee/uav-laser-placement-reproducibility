# UAV laser placement and optimal indoor experiment — reproducibility release

> **Complete package:** Download **uav_laser_public_release_optimal_20260820.zip** from the [v2026.08.20 release](https://github.com/JunaLee/uav-laser-placement-reproducibility/releases/tag/v2026.08.20). The archive preserves the executable code-and-data directory structure.

This package contains the minimum code and data needed to reproduce two parts
of the study:

1. true-`Snet` laser-placement optimization; and
2. the **optimal-layout only** indoor pipeline, using 11 calibration images and
   44 independent experiment images.

Parallel/worst layouts, cross-validation, test-set checkerboard evaluation,
Frobenius comparisons, stitching, segmentation, timing code, and paper-only
plots have intentionally been removed. A single minimal indoor-results figure
is retained so the released calibration and laser-only pose outputs can be
inspected directly.

## Requirements

Reference/development environment: MATLAB R2025b (64-bit). The packaged
entrypoints were code-analyzed, and the bundled placement preset, camera file,
and reference image were validated in R2025b. The archived numerical reference
comes from the previously completed production run; see `RELEASE_STATUS.txt`.
Required products are:

- MATLAB
- Computer Vision Toolbox
- Image Processing Toolbox
- Optimization Toolbox (placement optimization only)

No Symbolic Math, Statistics and Machine Learning, Parallel Computing, or
third-party toolbox is required.

## Quick start

Open MATLAB, change the current folder to this release root, and run one of:

```matlab
indoor = run_indoor_only;       % recommended first run
placement = run_placement_only; % choose saved preset or select a new Omega
allResults = run_all;           % placement choice, then indoor workflow
reference = run_placement_reference; % use the bundled 31-vertex preset
```

The indoor run creates `outputs/indoor_optimal`; the general placement runner
creates `outputs/placement`; and the preset reference runner creates
`outputs/placement_reference`. The placement search is substantially slower
than the indoor image pipeline. A MATLAB desktop is required only when a new
UAV area is selected interactively.

Open `placement_optimization/laser_placement_optimization.m` to inspect the
placement workflow. `run_placement_only` asks whether to use the bundled preset
or select a new area. In interactive mode, the user (1) draws the usable UAV
mounting polygon `Omega`, (2) clicks the camera optical-centre projection, and
(3) clicks one point in the positive camera-z direction. Double-clicking the
last polygon vertex completes the first step. The choice can be supplied
without a dialog as `run_placement_only("preset")` or
`run_placement_only("interactive")`.

## Data split and independence

The indoor data are frozen as follows:

- calibration: 11 images, original source indices
  `3, 4, 5, 7, 8, 9, 14, 18, 44, 50, 55`;
- experiment: 44 images, source indices `1–44`;
- resolution: 5280×2970 pixels for every image;
- calibration/experiment SHA-256 overlap: zero.

The 11 calibration images alone determine the camera intrinsics, distortion,
checkerboard poses, and two laser lines. The experiment code deliberately does
**not** detect the checkerboard in any of the 44 experiment images. Each test
image is processed only as

```text
raw image -> red/green centroid -> undistorted centroid
          -> closed-form laser pose -> homography -> orthorectified image
```

No stored centroid file (`R_cut`, `G_cut`, or similar) is read.

## Indoor method implemented

The checkerboard has size 10×15 with 15 mm squares. Camera calibration uses all
11 selected images, two radial coefficients, zero skew, and zero tangential
distortion.

For each calibration image, the red and green laser centroids are detected
directly in fixed, predeclared image windows. Centroids are undistorted. With
checkerboard pose `(zeta, theta)` and ray slope

```text
r = (i - cx) / fx,
z = zeta / (1 + r tan(theta)),
x = r z,
```

each laser line `p x + q z + 1 = 0` is fitted by the paper's direct least
squares equation `[x z] [p q]^T = -1`.

For an experiment frame, define `a_k = p_k r_k + q_k`. Pose is recovered
without iteration:

```text
tan(theta) = (a_1 - a_2) / (a_2 r_1 - a_1 r_2),
zeta       = -(1 + r_k tan(theta)) / a_k.
```

The image-to-surface homography is normalized to `H(3,3)=1`. The image is
undistorted once and warped to its laser-homography full footprint. Output is
limited to 1600 pixels per side and 3 megapixels; the actual millimetres per
pixel are recorded for every frame.

Minimal outputs are:

- `camera_parameters.csv` and `.mat`;
- `laser_coefficients.csv`;
- `calibration_qc.csv`;
- `experiment_results.csv` (centroids, pose, 3×3 homography, output scale);
- `orthorectified/frame_01...frame_44`;
- `optimal_indoor_results_plot.png` and the matching vector PDF, containing
  calibration geometry, raw centroid-x traces, recovered axial distance, and
  recovered surface angle for all 44 experiment images;
- `optimal_indoor_results.mat`, `reference_check.csv`, and `run_summary.txt`.

The indoor figure is deliberately laser-only: it does not plot checkerboard
ground truth or error metrics from the 44 experiment images.

## Placement inputs and reproducibility

`placement_optimization/data/campram3.mat` is the UAV camera model used for the
field of view and `Snet` mapping. `placement_optimization/data/m3.jpg` is the
planar reference photograph used to define the feasible mounting polygon
`Omega`. `placement_optimization/data/preset_uav_area.mat` contains only the
saved 31-vertex polygon and its selection metadata.

`run_placement_only` and `run_all` offer the saved preset and interactive
selection as explicit alternatives. `run_placement_reference` is the
click-free shortcut to the saved preset and writes a reference comparison to a
separate output folder. In interactive mode, image coordinates are rescaled to
the calibration size, undistorted with `campram3.mat`, and mapped to
millimetres by a planar projective transform. Because `m3.jpg` is a separate
reference photograph, this camera-model coupling should be treated as a stated
methodological limitation.

The allowable pose domain is the distance-dependent JHLEE `PI_dtheta` region.
The implemented objective is
`Snet = integral_PI_dtheta |det(J)| dtheta dd`; no independent constant theta
box is used, and feasible solutions with a folded mapping are rejected.

## R2025b numerical references

Placement:

- `Snet = 2,701,864.90342294 pixel^2`;
- laser 1 `(p,q) = (0.00222553183577613, -0.00283929246201715)`;
- laser 2 `(p,q) = (-0.00229057413314412, -0.00288666050726644)`.

Optimal indoor calibration:

- `(fx,fy) = (3711.89846886168, 3714.23909341637) pixel`;
- `(cx,cy) = (2654.09515654058, 1505.75713062106) pixel`;
- `(k1,k2) = (0.000563213947833881, -0.0187164618723344)`;
- mean reprojection error `0.513425960664668 pixel`;
- red `(p,q) = (0.00238118328949032, -0.00275392217518095)`;
- green `(p,q) = (-0.00230623436069604, -0.00275037855399832)`.

Small platform/version-dependent numerical differences are possible. Both the
indoor runner and the saved-preset reference runner write an
expected-versus-actual table and warn on a material change. An interactive
placement run has no fixed numeric target because its `Omega` is user-defined.

## Integrity and metadata

`metadata/DATA_MANIFEST.csv` records the original byte hash, release byte hash,
and decoded-RGB hash for every image. Public image copies have embedded JPEG
APP/COM metadata (including EXIF/XMP telemetry) removed without JPEG
recompression; unused auxiliary JPEG trailers were also removed. Decoded
primary-image pixels are unchanged.
`SHA256SUMS.txt` freezes the complete release payload. Verify it with:

```bash
python verify_release.py
```

The filenames and manifest are package-relative; the code contains no user or
Dropbox absolute paths.

## Licenses

The MATLAB and Python source files are released under the MIT License; see
`LICENSE`. The image data, tabular data, reference outputs, figures, and
documentation are released under CC BY 4.0; see `DATA_LICENSE.md`. MATLAB and
MathWorks toolboxes are not distributed with this package.
