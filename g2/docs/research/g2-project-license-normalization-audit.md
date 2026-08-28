# G2 project-source MIT normalization audit

The baseline overlay/license inventory contained 459 unique source records
classified as project-owned or adapted, labeled GPL, and carrying no upstream
record: 321 `GPL-3.0-only` and 138 `GPL-3.0-or-later`. The project-authored LZ4
ABI wrapper was a 460th overlay target after its misleading provider pointer
was reviewed. All 460 now carry MIT source declarations and matching
content-addressed overlay pins.

This mechanical normalization must preserve genuine upstream licensing. The
only genuine upstream GPL source is `ring_gesture.c` from g2flash. The thin
OpenCFW LZ4 ABI wrapper is project-authored and is therefore an MIT target;
the separately retained LZ4 implementation remains BSD-2-Clause. The current
inventory also has 80 Apache-2.0 records, 97 BSD records, seven ISC records,
and 27 Zlib records;
the audit holds those upstream/provider records outside the MIT rewrite set.
In particular, reviewed AmbiqSuite realizations that carry
authenticated BSD provenance remain BSD rather than being relabeled MIT.

The overlay inventory is not the complete public source bundle. The broader
exact distributed-source census now contains 834 distinct project-authored
files. It combines the original 729-file scope (720 component/tool/test paths,
eight research artifacts, and the OpenCFW LZ4 ABI wrapper) with 97 reviewed
community controller/build-adapter paths; one case source occurs in both
sets. Every path has an SPDX expression permitting MIT. The one authenticated
upstream GPL source is excluded from this target set. This includes project
tests, fixtures, tools, Java research utilities, machine-readable source
records, the Touch/Case/GX8002/EM9305 community controller sources, and the
canonical Apollo-core and liblc3 build adapters. Five `MIT OR GPL` files
already permit MIT and are recorded separately rather than treated as
blockers.

The census also covers all six files in the open Touch source-image package,
its project-authored proof analyzer, and both focused source-image tests. The
package README and linker script are included alongside its C, header, and
Python build sources, so documentation or link-policy license regressions fail
closed rather than falling outside the source audit.

The community controller closure is exhaustive over 100 C, header, assembly,
and Python files: 97 project-authored MIT-compatible paths plus three retained
Apache-2.0 Touch adaptations (`runtime_touch_cat2_adapters.c/.h` and
`runtime_touch_critical_adapters.S`). The Apache files remain outside the MIT
rewrite set and retain their upstream-compatible provider terms.

The machine-readable census remains immutable after normalization so future
GPL or missing-license regressions fail closed. The analyzer recomputes every
source declaration, overlay license, source size/hash pin, and the single
preserved GPL provenance record; it now reports zero pending rows.

Artifacts:

- `tools/analyze_g2_project_license_normalization.py`
- `tools/manifests/g2-project-license-normalization.tsv`
- `tools/manifests/g2-project-license-normalization-summary.json`
- `tools/manifests/g2-project-mit-normalization-community-controllers.txt`
- `tools/manifests/g2-project-mit-normalization-touch-source-image.txt`
- `tests/test_analyze_g2_project_license_normalization.py`

This is a software-only provenance audit. Hardware validation remains deferred
by project direction, and the audit performs no build, MMIO, reset, signing,
flashing, or production-file mutation.
