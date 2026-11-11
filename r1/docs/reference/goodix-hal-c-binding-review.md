# R1 Goodix public I2C HAL bound to checked C transport

The normal R1 application composition now resolves the SDK's three public I2C
HAL entries through the checked native R1 transport. Application imports fall
from 210 to 207: `gh3026_i2c_init`, `gh3026_i2c_write`, and `gh3026_i2c_read`
are removed, with no additions. Other unproven SDK board hooks remain explicit.

| Public HAL | R1 body | Stock evidence |
| --- | --- | --- |
| `hal_gh3x2x_i2c_init` | `r1_goodix_i2c_open` | `0x6f8f6` tail-calls `0x509b0` |
| `hal_gh3x2x_i2c_write` | `r1_goodix_i2c_write` | `0x6f90e`; registered by `0x2d87c` through `0x2aaf8` |
| `hal_gh3x2x_i2c_read` | `r1_goodix_i2c_read` | `0x6f8fa`; registered alongside write |

The [transport review](goodix-i2c-c-transport-review.md) and its retained REA
snapshot establish the actual I2C callback registration and native bodies.
The init tail branch is present in the locked artifact's raw Thumb code.
SDK parameter and return types are used explicitly (8-bit address/status,
16-bit lengths, byte-buffer pointers). GNU C aliases share each body; no new
forwarding function, success-only stub, or duplicate stock implementation is
introduced. The read body retains the native command-halfword access.

`sources.json` generates `gh_demo_user_r1.c` from the pinned upstream
`gh_demo_user.c`. Exactly three superseded I2C function definitions are
removed. Each replacement requires exactly one matching source span, so
upstream changes fail generation rather than silently selecting another body.
The original vendor file is unmodified. The generated unit explicitly includes
`kernel/gh_demo_config.h` to preserve the original sibling-header selection;
moving the source must not activate the separate driver configuration overlay.

Object comparison against the preceding build confirms that all 25 remaining
nonempty executable sections of the demo unit have unchanged bytes. Exactly
the three I2C sections disappear. SDK declarations and the R1 definitions
compile together without conflicting types. The three aliases have identical
symbol value, size and section to their respective implementations.

Stock execution comparisons pass through the public HAL symbols (630 cases),
as well as the native transport symbols (630), binding/reset sequences (1,536),
IRQ paths (2,592), and first transfers from stock startup data (eight). The
linked initializer still matches all 36 adjacent stock cold-state bytes.
The full build `build/sources-goal-r1-goodix-hal-binding/report.json` compiles
564 units without failures or duplicate strong symbols; imports are now
207 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-hal-c-binding-review.json) binds the build, source,
generated input, ABI/section audit and execution probes by hash.

This is source-level I2C integration, not whole-image byte qualification.
Alias sharing does not reproduce the separate four-byte stock init thunk.
The canonical source plan remains unchanged. Remaining SDK GPIO/reset/gsensor
hooks, complete vendor configuration equivalence, final source linking,
physical I2C behavior and full firmware byte identity remain unproven. G2
workflow gates are unchanged.
