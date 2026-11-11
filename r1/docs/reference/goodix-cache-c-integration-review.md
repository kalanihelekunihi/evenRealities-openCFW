# R1 Goodix shared cache and reset integration

The I2C transport now consumes `r1_ppg_bus_device`, the existing owner of stock
cell `0x200076cc`. Its previous separate `r1_goodix_i2c_device` definition was a
duplicate native-state owner: isolated transport tests supplied that cell
directly and did not exercise binding. That definition is removed. Binding and
transport now share one C symbol and one linker section.

REA confirms stock `0x50944` already corresponds to the existing
`r1_ppg_device_bind` in `native_peripheral_bindings.c`. It lazily looks up
`i2c_4`, `ppg_int`, and `ppg_reset_en` in that order, stores the results in
`0x200076cc`, `0x200076d0`, and `0x200076d8`, and opens the reset device through
slot 08. Existing nonzero handles bypass lookup. No second initializer was
added.

Three additional native wrappers now compile as C in
`r1/src/application/goodix/stock_i2c_transport.c`:

| Entry | Candidate | Observed dispatch |
| --- | --- | --- |
| `0x509a4` | `r1_goodix_i2c_close` | Bus handle, slot 0c |
| `0x50ae0` | `r1_goodix_power_enable` | Reset handle, slot 18, words 1 and 0 |
| `0x50af0` | `r1_goodix_power_disable` | Reset handle, slot 18, words 0 and 0 |

The historical power names are retained; the accessed device is specifically
`ppg_reset_en`. Electrical power sequencing is not inferred from those names.

The ignored probe `build/goal-r1-goodix-cache/verify.py` passes 1,536 paired
sequences, or 21,504 native/C entry executions. Each sequence runs binding,
bus open, write, read, reset enable, reset disable, and bus close. It executes
the actual native/reconstructed registry lookup and dispatch bodies, while
modeling string equality and final device operations. Cases cross all eight
initial handle masks, all eight registry availability masks, present/absent
operations, operation success/error, null/non-null data buffers, and three
length/command values. Comparison covers cache/request read and write order,
lookup strings, operation arguments, retained request bytes, preserved
registers, stack restoration and interrupt masks. The original 630 transport
comparisons also pass with the canonical owner linked from the board module.

The full R1 build at `build/sources-goal-r1-goodix-cache-final/report.json`
passes: 563 units, no compile failures or duplicate strong symbols, and
unchanged imports (210 application, 34 bootloader). `make sources-check`
passes. [Machine evidence](goodix-cache-c-integration-review.json) records
source, verifier, report, REA snapshot, manifest and source-plan hashes.

The canonical source plan is unchanged. These are behavioral candidates, not
byte-qualified providers. Physical I2C/reset behavior, concurrency, full
invalid-pointer coverage, final linking/placement and SDK `gh3026_*` hook
integration remain unproven. G2 workflow gates were not advanced.
