# UAV laser placement and optimal indoor experiment — reproducibility release

> **Complete package:** Download **uav_laser_public_release_optimal_20260818.zip** from the [v2026.08.18 release](https://github.com/JunaLee/uav-laser-placement-reproducibility/releases/tag/v2026.08.18). The archive preserves the executable code-and-data directory structure.

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
entrypoints were code-analyzed and numerically cross-checked against the prior
executed R2025b pipeline. A clean end-to-end batch rerun is still pending
because this host currently fails before MATLAB startup; see
`RELEASE_STATUS.txt`. Required products are:

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
placement = run_placement_only; % interactively select Omega from m3.jpg
allResults = run_all;           % interactive placement, then indoor workflow
reference = run_placement_reference; % optional fixed-Omega reference run
```

The indoor run creates `outputs/indoor_optimal`; the interactive placement run
creates `outputs/placement_interactive`; and the fixed-reference runner creates
`outputs/placement_reference`. The placement search is substantially slower
than the indoor image pipeline. `run_placement_only` and `run_all` require a
MATLAB desktop because they wait for user clicks.

Open `placement_optimization/placement_optimization_true_Snet.mlx` to inspect
the placement workflow. Its public default is
`UAVLaserConfig.InteractiveSelection=true`. The user (1) draws the usable UAV
mounting polygon `Omega`, (2) clicks the camera optical-centre projection, and
(3) clicks one point in the positive camera-z direction. Double-clicking the
last polygon vertex completes the first step. The plain-text source beside the
MLX is executable and code-equivalent to it.

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

`campram3.mat` is the UAV camera model used for the field of view and `Snet`
mapping. `m3.jpg` is a separate planar reference photograph used historically
to define the feasible mounting polygon `Omega`; it was not acquired by the
UAV camera represented by `campram3.mat`.

The public MLX, `run_placement_only`, and `run_all` default to interactive
selection from `m3.jpg`, as described above. For a click-free numeric reference,
run `run_placement_reference`; it uses the archived eight-vertex `Omega`
coordinates in millimetres and writes to a separate output folder. In the
interactive path, this rollback intentionally preserves the pre-20:00 legacy
implementation: image coordinates are rescaled to the `campram3.mat`
calibration size, undistorted with that camera model, and then mapped to
millimetres by a planar projective transform. Because `m3.jpg` is a separate
reference photograph, this legacy camera-model coupling is retained solely for
reproducing the earlier optimization result and should be treated as a stated
methodological limitation.

The implemented objective is the mapped geometric area
`Snet = integral_Phi |det(J)| dtheta dzeta`; feasible solutions with a folded
mapping are rejected.

## R2025b numerical references

Placement:

- `Snet = 3,819,388.271913765 pixel^2`;
- laser 1 `(p,q) = (0.002413814899295697, -0.002816187380011802)`;
- laser 2 `(p,q) = (-0.002413814886238418, -0.002817325277933838)`.

Optimal indoor calibration:

- `(fx,fy) = (3711.89846886168, 3714.23909341637) pixel`;
- `(cx,cy) = (2654.09515654058, 1505.75713062106) pixel`;
- `(k1,k2) = (0.000563213947833881, -0.0187164618723344)`;
- mean reprojection error `0.513425960664668 pixel`;
- red `(p,q) = (0.00238118328949032, -0.00275392217518095)`;
- green `(p,q) = (-0.00230623436069604, -0.00275037855399832)`.

Small platform/version-dependent numerical differences are possible. Both
the indoor runner and the fixed-Omega reference runner write an
expected-versus-actual table and warn on a material change. The interactive
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

