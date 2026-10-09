# Unchanged PDL compiler discrimination

Three official Arm GNU Linux archives were downloaded from the vendor URLs
already pinned in `tools/bootstrap/versions.json`; all archive SHA-256 checks
passed before extraction. Exact URLs, archive/compiler hashes are in
`acquisition.json`. Nothing replaces host defaults. Tool trees and outputs are
locally ignored inside this isolated task directory; durable receipts remain
visible repository artifacts.

The unchanged PDL source SHA-256 is
`2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07`,
pin `35f1714623cfea682d5e285af80d50416b4c7bbc`. Recorded flags are
`-mcpu=cortex-m0plus -mthumb -Og -ffreestanding -fno-builtin
-DCY8C4046FNI_T412 -ffunction-sections`, with the same PDL/CMSIS/core-lib
include families and system-header stub as the prior 13.3 experiment.
Consumed input hashes and compiler-specific headers are recorded per build.

| Compiler | Configure 424 bytes | Capture 48 bytes | ConfigureScan 160 bytes |
| --- | --- | --- | --- |
| 10.3.1, release 10.3-2021.10 | 424 bytes; 173 differing positions | exact | 160 bytes; 30 differing positions |
| 11.3.1, release 11.3.Rel1 | 424 bytes; 125 differing positions | exact | exact |
| 12.2.1, release 12.2.Rel1 | 424 bytes; 125 differing positions | exact | exact |
| prior 13.3.1 receipt, not rerun | 424 bytes; 24 differing positions | exact | exact |

All compared sections have no relocation entries. Comparisons use complete
sections against the original touch image (32-byte payload header removed,
flash base `0x3300`): Configure `0x8FD0`, Capture `0x8FA0`, ConfigureScan
`0x9178`. Each build retains object, preprocessed input, assembly and dependency
file; hashes are in `results.json`. This is compiler execution, not firmware or
original-instruction execution.

These results narrow the proposed older-GCC explanation: none of the three
older releases closes Configure's mismatch, and 10.3 also fails an independent
peer. Under this exact source/header/flag environment, 11.3/12.2 remain
compatible with the two peers while 13.3 is a closer Configure comparator.
No unique producing compiler, private source modification, generated cycfg or
whole-image equality follows. The next useful discriminator is the exact
Configure loop source/translation-unit environment, not another duplicate
13.3 optimization sweep.

Docker uses the documented digest-pinned Ubuntu base, linux/amd64, no network,
all capabilities dropped and no-new-privileges. Tool, PDL and required header
trees are read-only mounts; only this task's version-specific output directory
is writable. No privileged container, devices, home-wide mount or socket mount
is used. Initial PDL mount under `/tmp` was unavailable inside Colima, producing
an ordinary missing-source error; an authenticated source copy inside the task
directory supplied the same source without changing original files. Approved
sandbox escalation provides Docker access; socket permissions were untouched.

Independent receipt review and campaign admission remain pending. No campaign
state, gates, source implementations, Git index or devices were changed.
