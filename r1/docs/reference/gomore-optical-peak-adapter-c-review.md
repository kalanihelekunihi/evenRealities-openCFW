# GoMore optical peak stage in C, 2026-11-10

`r1/src/application/runtime/native_gomore_optical_peak_adapter.c` supplies
the stock `0x60af4` four-argument ABI. Typed C callbacks connect the existing
source-owned filter configuration, linear resampler and filter application to
`gomore_primitives_sleep_optical_peak_update`. The GoMore C owner now
continues to trim and encode when valley selection yields an empty candidate
list. Stock writes the empty record marker in that case; the earlier C
short-circuit left it zero.

An ignored Unicorn replay under
`build/r1-gomore-optical-peak-adapter-20261110/` compares the SHA-pinned
official R1 2.2.6.0009 stage with the adapter and C GoMore owner.
**1,024 paired cases pass** for elapsed block counts 0–3, valid and invalid
sample records, 0–12 prior positions, randomized history and sample values,
all four rounding modes, FZ/DN settings and sticky flags. Return values,
all 396 state bytes, the 24-byte output window and FPSCR match; SP and saved
registers are checked. The cases execute all **55 of 55** stock instruction
starts in the 140-byte stage. The manifest adapter exactly matches the
replayed C object's allocated sections (90 bytes) and 11 relocations; the
vendor object also matches the replayed C object's allocated sections and
relocations. The replay binds the lower filter configuration, resampler,
filter application and memory-clear routines to stock; physical optical
input and integrated source versions of those providers remain unverified.

The R1-only build at
`build/sources-r1-gomore-optical-peak-20261110/report.json` compiles 891/891
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict bootloader link is vector-valid. The strict
application receipt at
`build/sources-r1-gomore-optical-peak-20261110/app-link/report.json` has
**26 undefined functions**, one fewer than before. Its full flash load
exceeds the configured span by **28,840 bytes**, 64 bytes more than the
preceding checkpoint. The application executable remains incomplete.
