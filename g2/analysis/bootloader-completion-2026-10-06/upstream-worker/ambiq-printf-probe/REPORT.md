# Ambiq printf hypothesis — bounded first test

14/14 integer-format fixtures match output bytes and return count between original stock Thumb parser `0x415bf6` and host-compiled SDK `am_util_stdio_sprintf`. Changed-argument and changed-count negative controls reject. The test uses the authenticated bootloader and records visited original instructions in `comparison.json`.

SDK input: `third-party/local-vendor/sources/AmbiqSuite_R3.2.0/utils/am_util_stdio.c`, revision `release_sdk_3_2_0-dd5f40c14b`, retaining its Ambiq 2024 BSD-3-Clause notice in the unchanged ignored vendor tree. No source copied or license removed. Its source and the compiled library hashes are in the receipt; a package version alone is not producing-source proof.

Compile locally without hardware or vendor compiler activation:

```sh
clang -dynamiclib -O0 -I third-party/local-vendor/sources/AmbiqSuite_R3.2.0/utils third-party/local-vendor/sources/AmbiqSuite_R3.2.0/utils/am_util_stdio.c -o /tmp/opencfw-ambiq-printf.dylib
/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiq-printf-probe/probe.py
```

Fixtures cover literals, zero/negative decimal, unsigned maximum, lowercase/uppercase hex, width/zero padding, negative zero-padding, character, literal newline, percent escape, mixed integer arguments and unknown `%q`. Stock executes its actual parser/helpers with synthetic argument memory. SDK executes native host code with host varargs; the test intentionally excludes pointer/string, 64-bit and float cases until their different ABI representations are handled. Translation remains false; sink wrapper and null-sink paths are not tested. This is behavioral correspondence for these cases, not exact compiler output, 11-body source closure or production buffer-safety certification.

Next bounded extension: explicit ARM variadic alignment fixtures for 64-bit and float values; precision/string handling and translation-enabled output; sink callback order/return. Only after those checks should a firmware-source adaptation be integrated.
