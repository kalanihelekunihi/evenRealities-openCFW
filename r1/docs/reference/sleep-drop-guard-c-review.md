# R1 sleep record drop guard in C

The application implementations in `native_wear_sleep_status.c` and
`native_sleep_wake.c` reconstruct stock functions `0x4c6c0` and `0x4a3e8`
from the SHA-256-pinned R1 2.2.6.0009 application. The getter reads the
already-owned wear sleep latch (`0x20006e96` in stock), while the guard
accepts a type-1 final sleep record only if its encoded stage count at
bytes 30–31 is nonzero. It rejects other records when the latch is zero,
with the stock ring/SDK log gates and text. This is ordinary C, without an
embedded executable copy or an assembly bridge.

The ignored fixture at `build/r1-sleep-guard-probe-20261110/compare.py`
loads the stock binary and a linked C object in separate Cortex-M4 Unicorn
instances. It compares return value and ring/SDK log calls for 512 paired
cases: latch 0/1/2/255, mode bits 0–7, record type 0/1/2/255, and stage
count 0/1/256/65535. All 512 matched; the result is in `result.json`.
The fixture models the logging providers and does not establish physical
sensor behavior or byte identity.

`make sources-check` passes at 963 R1 units/750 source files with none
unbuilt. The source composition compiles 881 application and 82 bootloader
units with no duplicate strong symbols. The strict bootloader link has no
undefined references and a valid vector. The strict application link still
has 39 undefined symbols and exceeds flash capacity by 29,992 bytes
(`build/r1-sleep-guard-c-final-20261110/app-link/report.json`). The two
newly sourced functions are not direct application link imports, so the
undefined count remains unchanged. `git diff --check` passes.
