# Matching tools

These tools identify the original compiler and flags, and check rebuilt
functions against stock bytes, using open toolchains wherever possible.

- `compare_function.py` compares one compiled function (from a
  `-ffunction-sections` object) with its stock bytes. It prints MATCH, or a
  side-by-side disassembly.
- [`experiments.md`](experiments.md) records each compiler-identification
  experiment: inputs, the matrix tried, the result, and what it implies for
  [`../../MISSING-TOOLCHAIN.md`](../../MISSING-TOOLCHAIN.md).

The toolchains come from [`../bootstrap/`](../bootstrap/README.md): Arm GNU
6-2017-q2, 7-2018-q2, 8-2019-q3, 9-2020-q2, 10.3-2021.10 and 13.3.Rel1.
Distribution LLVM 14–20 and the C-SKY and ARC GNU tools are installed as
listed under `system_packages` in `versions.json`.
