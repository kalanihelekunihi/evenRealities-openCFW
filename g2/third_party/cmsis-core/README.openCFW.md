# Arm CMSIS Core header closure

This subtree contains the seven unmodified CMSIS Core headers reached when
compiling the pinned AmbiqSuite Apollo510 MSPI translation unit. They come
from the official
[`ARM-software/CMSIS_5`](https://github.com/ARM-software/CMSIS_5)
repository at commit
`d23a6949a0331ca96853bcd98b0fdcc4db47184c`.

That commit is selected because its `core_cm55.h` and `cmsis_version.h`
SHA-256 values exactly match the version-aligned closure used by the
successful Apollo510 ABI/section-GC proof:

- `core_cm55.h`:
  `23c98f9996ce044c7a4a3affe4d7be36d15c67d4a1389d604e06d02672bdb1d7`
- `cmsis_version.h`:
  `184c19fd3ee73632edf35a0b4d49cd48be75fbf49e6ccb19d9db05fa83bea4b3`

`PROVENANCE.json` pins every imported file by size, Git blob SHA-1, and
SHA-256. `verify_snapshot.py` performs an offline integrity check.

CMSIS_5 is licensed under Apache-2.0. The unmodified upstream license is in
`LICENSE.txt`.
