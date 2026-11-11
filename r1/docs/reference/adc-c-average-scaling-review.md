# Battery ADC averaging and scaling reconstructed in C

`stock_battery_average.c` owns stock averaging `0x50c90` and integer scaling
`0x50d00`. The existing VNFC rectified-ADC owner supplies the volatile ADC handle
at native `0x20006854`; no duplicate cache cell is introduced. See the
[binding correction](vnfc-adc-binding-review.md). The earlier fixture used
different stock/source cells and did not establish correct handle ownership.

A fourteen-byte bridge preserves the average routine's exact exposed entry
frame: eight saved words at caller SP minus 32, with the sample halfword
aliasing saved R3. The C kernel clears only that halfword, preserving its high
half and other saved words. It opens the ADC, makes ten cycle-delay calls with
argument 64,000, then makes three driver reads with operation zero, the sample
pointer and count one. Each read uses a fresh handle load. Negative samples
are clipped by a halfword zero store; the sample is read again for summation
and cleared after each read, including the last. Close also reloads the handle.
Driver statuses do not short-circuit this native sequence. The result is the
signed sum divided by three and narrowed to sixteen bits.

The arithmetic routine preserves native unsigned multiply/add wrap and the
sixteen-bit extraction: `scaled = ((raw * 3600 + 2048) >> 12) & 0xffff`, followed
by `(scaled * 331 / 51) & 0xffff`. Its historical symbol says percent, but the
implementation does not clamp or claim a 0..100 result. C replaces all arithmetic
and averaging policy; assembly remains only in the saved-frame bridge.

The stock/C probe passes 224 averaging cases (448 executions), covering seven
sample triples, halfword/full-word/byte/no-write driver effects, live handle
mutations, two saved-R3 seeds and driver success/error returns. It compares
ordered handle/frame accesses, complete driver-visible saved frames for the
standalone average, delay/read/close sequence, output, final handle and preserved
registers/stack/masks. All 65,536 scaling input words pass paired comparisons
against stock with the average boundary modeled.

Another 224 cases execute actual native/C average and scaling together. These
compare declared sample-halfword effects, external arguments, handle changes
and outputs. Converter private saved-register values and internal code return
addresses differ, so arbitrary driver overreads of that caller frame are not
covered. The harness records this limitation rather than presenting isolated
arithmetic success as complete integration identity. Negative controls removing
clipping or widening the sample clear to a word both fail.

The full report `build/sources-goal-r1-adc-average/report.json` compiles 571 R1
units without failures or duplicate strong symbols. Imports remain 197
application and 34 bootloader. `make sources-check` passes.
[Machine evidence](adc-c-average-scaling-review.json) binds REA, source, shared
context header, execution probes, negative controls and normal build by hash.

The C averaging kernel is 116 bytes plus its fourteen-byte bridge; native has
104 instruction bytes. C scaling is 42 bytes, equal in size to stock but not
byte-qualified. The canonical source plan and G2 gates are unchanged. Driver
and delay boundaries are modeled: actual cycle timing, including native loop
and NOP instruction scheduling, ADC electrical behavior, arbitrary aliases,
concurrency and complete source-only byte identity remain unverified.
