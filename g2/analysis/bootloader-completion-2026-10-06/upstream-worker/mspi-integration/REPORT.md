# Public MSPI provider closure for bootloader NOR setup

This is a compile/link dependency probe for the already implemented call flow;
it does not replace any bootloader provider or change the shared components.

## Call path and reusable functions

`inventory-worker/nor-read-setup/nor_read_setup.c` models the stock NOR setup
at `0x420e08` and caller at `0x420e8c`. Its linker map binds
`opencfw_bl_mspi_disable`, `opencfw_bl_mspi_device_configure`,
`opencfw_bl_mspi_enable`, and `opencfw_bl_mspi_control` to stock addresses
`0x4250f0`, `0x424be4`, `0x425066`, and `0x4251c0` respectively. The observable
sequence is disable → device configure → enable → control request `0x18` with
clock value `16`. The configure/enable/control functions are not yet locally
source-owned in the existing `foundation/ambiq_mspi` component.

Reuse already available in-tree:

| Stock entry | Reusable implementation/evidence | Remaining seam |
|---|---|---|
| `am_hal_mspi_disable` (`0x4250f0`) | Exact unchanged BSD-3-Clause body in `foundation/ambiq_mspi/ambiq_mspi_lifecycle.c`; exact pinned source/function hashes in `SOURCE_PROVENANCE.json`; independently compared against stock | Local CQ disable/term wrappers and `am_hal_delay_us`; CMDQ source only covers a bounded provider profile, not all SDK services |
| `am_hal_mspi_device_configure` (`0x424be4`) | Public pinned HAL source is available under this owned acquisition at the recorded commit; compile succeeds | No stock behavioral/source correspondence established; public handle/state/config ABI cannot be assumed compatible |
| `am_hal_mspi_enable` (`0x425066`) | Public pinned HAL source is available and compiles | No stock correspondence established; public source calls `am_hal_cmdq_init` and operates on its own full state model |
| `am_hal_mspi_control` (`0x4251c0`) | Public pinned HAL source is available and compiles | No stock correspondence established; generic switch retains dependencies for many requests, including paths not taken by NOR setup |

The public source is Apollo510 HAL5.1.0 at
`5efc0228528a8adce5eae0d226fac85d2551eb3b`; the copied replay's file hash is
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`.
Acquisition/license evidence lives in `../ambiqhal-apollo510/PROVENANCE.md`
and its per-file provenance tables. It is a public source candidate, not proof
that stock bootloader functions came from this checkout.

## ABI constraints found before integration

The public HAL header enumerates `AM_HAL_MSPI_REQ_XIP_CONFIG` as `0x10` and
`AM_HAL_MSPI_REQ_CLOCK_CONFIG` as `0x18`; the latter's pointer type is
`am_hal_mspi_clock_e *`. Thus stock call `0x420e8c → control(0x18, &clock)`
has a direct public-header type match. The preceding NOR setup's request `0x10`
passes the object at `0x20000204` after writing byte offset5; the public
request expects a 20-byte `am_hal_mspi_xip_config_t`. Available call evidence
does not establish the complete stock object's extent/layout, so this remains
a plausible pointer contract rather than a confirmed layout match.

More importantly, the public HAL's full `am_hal_mspi_state_t` and global state
model are not the stock layout. The existing compatibility header documents
this and uses only specifically recovered sparse offsets for lifecycle
functions. Directly compiling the public full source against a stock handle
would therefore be unsafe without a separately proven adapter/state mapping.
The public `am_hal_mspi_device_configure` accepts
`am_hal_mspi_dev_config_t`, whose pinned header layout is 52 bytes on the
32-bit ARM target (Clang record-layout dump). The stock caller constructs and
passes a 24-byte buffer. This is a concrete ABI mismatch: the public function
reads fields beyond that buffer, so it cannot safely replace stock
`device_configure` as-is. A different adapter/provider is required unless the
stock function's private layout is separately recovered and translated. Keep
the four stock address bindings until those contracts are
resolved or the original function bodies have their own reviewed source
reconstruction.

## Relocatable link probe

`call_slice.c` calls the four APIs in the evidenced order and includes both
requests `0x10` and `0x18`. The local Makefile compiles the exact pinned public
`am_hal_mspi.c` for Cortex-M55/Thumb/soft-float and section-garbage-collects
unrelated exported functions while retaining the four-entry call slice.
`layout_probe.c` has static assertions for the public 52-byte device-config
and 20-byte XIP-config types; `arm-none-eabi-nm -S out/layout_probe.o`
confirms symbol sizes `0x34` and `0x14`. Run `make` in this directory; it
leaves the relocatable object, layout probe object, and sorted undefined-symbol
list in `out/`. This is a real ARM relocatable link, not a runnable ELF:
external providers intentionally remain unresolved.

Observed external cut (`out/undefined-symbols.txt`):

```text
am_hal_clkmgr_clock_release
am_hal_clkmgr_clock_release_all
am_hal_clkmgr_clock_request
am_hal_cmdq_alloc_block
am_hal_cmdq_disable
am_hal_cmdq_enable
am_hal_cmdq_error_resume
am_hal_cmdq_get_status
am_hal_cmdq_init
am_hal_cmdq_post_block
am_hal_cmdq_post_loop_block
am_hal_cmdq_release_block
am_hal_cmdq_reset
am_hal_cmdq_term
am_hal_delay_us
am_hal_delay_us_status_check
am_hal_interrupt_master_disable
am_hal_interrupt_master_set
am_hal_pwrctrl_periph_disable
am_hal_pwrctrl_periph_enable
```

`device_configure` and helpers account for the clock-manager, interrupt-mask,
and delay edges. `enable` needs CMDQ initialization. `disable` needs the two
CMDQ teardown functions plus delay; the in-tree reconstructed bounded CMDQ
profile covers its `mspi_cq_disable`/`mspi_cq_term` layer, not every public
`am_hal_cmdq_*` symbol. `control` is one monolithic function containing many
request branches, so its relocatable-object cut includes CMDQ block/post/status
operations, extra clock manager and power-control operations, and delay
helpers used by other control requests. Those are link-time dependencies even
though this caller passes only requests `0x10` and `0x18`.

This cut is scoped to the generic public API object and the selected call
sequence; it is not the minimal runtime path for two constant request values.
Resolving it by supplying SDK files would still not cure the stock-state and
configuration ABI gaps. Root NOR setup can continue using the authenticated
stock-call aliases while the remaining wrapper logic is source-owned.

## Reproduction

```sh
cd g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-integration
make
cat out/undefined-symbols.txt
```

No device, proprietary key, SDK agreement payload, or hardware was used for
this probe.
