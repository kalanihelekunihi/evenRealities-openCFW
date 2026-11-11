# Raw/scaled ADC pair reconstructed in C

REA confirms stock `0x50d2a` calls the average routine, stores its low halfword
at output offset zero, then calls the scaling routine and stores its low
halfword at offset two. Scaling performs a second independent ADC average.
The historical `r1_temperature_pair_read` name is retained for source mapping;
this routine's observed dependencies are the battery ADC average and scaling
functions, not the separate GXT310 temperature driver.

The C implementation in `stock_battery_average.c` preserves two acquisitions
and two ordered volatile halfword stores. It does not reuse the first reading
for scaling. The first store precedes the second acquisition, and a mutation
of the already-stored first output during that acquisition survives the final
second-output store. No new state owner or unresolved provider is introduced.

The pair probe passes 384 paired stock/C cases (768 executions): independently
varied first/second average words, two output seeds and three modeled mutation
policies at the acquisition boundaries. It checks two calls, first-output
visibility before the second call, actual native/C integer scaling (including
compiler inlining), exact halfword write widths/values, output canaries and
preserved registers/stack/masks. Unicorn's write-hook value is narrowed to the
actual store width; an untruncated register operand is not a wider memory write.
The average boundaries are modeled in these pair comparisons, so they do not
establish physical ADC acquisition behavior.

All 224 standalone average and all 65,536 scaling regression cases pass against
the updated object. A deliberate shortcut acquiring once and scaling its cached
first result fails: first average one and second average 4095 must yield two
acquisitions and scaling of 4095. The variant makes one acquisition.

The normal report `build/sources-goal-r1-adc-pair/report.json` compiles 571 R1
units without failures or duplicate strong symbols. Imports remain 197
application and 34 bootloader. `make sources-check` passes.
[Machine evidence](adc-c-pair-review.json) binds REA, source, execution probes,
negative control and normal build by hash.

The compiled C pair is 50 bytes versus 18 native instruction bytes because
scaling is inlined. No byte qualification was performed. The canonical source
plan and G2 gates remain unchanged. Private frames, caller-clobbered registers
and flags, arbitrary aliases/faults, concurrency, physical ADC/timing behavior
and complete source-only byte identity remain unverified.
