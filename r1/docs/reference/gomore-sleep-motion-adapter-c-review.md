# GoMore three-axis sleep motion stage in C, 2026-11-10

`r1/src/application/runtime/native_gomore_sleep_motion_adapter.c` supplies
the stock `0x5f3d8` four-argument ABI. It reads the three channel pointers
and unavailable flag from the caller's 13-byte input record, then calls the
existing source-owned `gomore_primitives_sleep_motion_feature` with the
source-owned floor and square-root providers. The stage body and adapter are
ordinary C. The GoMore C owner now tests its warmup count as signed, matching
the stock `int` comparison for values with the high bit set.

The ignored Unicorn replay under
`build/r1-gomore-sleep-motion-adapter-20261110/` compares the SHA-pinned
official R1 2.2.6.0009 stage against the adapter plus its C GoMore owner.
**4,096 paired cases pass** over available/unavailable inputs, modes 0–3,
warmup counts 0, 1, 4, 5, 6 and `0xffffffff`, randomized filter histories,
thresholds and three-axis samples, four rounding modes, FZ/DN settings and
sticky flags. Return values, all 128 state bytes, output bytes and FPSCR
match; SP and saved registers are checked. The cases execute all **80 of 80**
stock instruction starts in the 222-byte stage. The source object matches
the replayed adapter's 64 allocated bytes and four relocations; the vendor
object also exactly matches the replayed C object's allocated sections and
relocations. The replay binds the lower linear resampler, floor, square-root
and memory-clear routines to stock, so integrated source versions, physical
sensor data and timing remain outside this proof.

The R1-only build at
`build/sources-r1-gomore-sleep-motion-20261110/report.json` compiles 890/890
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict bootloader link is vector-valid. The strict
application report at
`build/sources-r1-gomore-sleep-motion-20261110/app-link/report.json` has
**27 undefined functions**, one fewer than before. Its full flash load
exceeds the configured span by **28,776 bytes**, 64 bytes more than the
preceding checkpoint. The application executable remains incomplete.
