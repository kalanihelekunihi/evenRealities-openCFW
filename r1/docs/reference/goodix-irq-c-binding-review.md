# R1 Goodix IRQ binding in C

Two native IRQ-device functions now compile from
`r1/src/application/goodix/stock_i2c_transport.c` without inline assembly:

| Stock entry | Candidate | Observed behavior |
| --- | --- | --- |
| `0x50ab0` | `r1_goodix_irq_close` | Load cached IRQ handle; return slot-0c status |
| `0x50abc` | `r1_goodix_irq_prepare` | Open IRQ device; conditionally bind callback through slot 20 |

REA and raw Thumb instructions establish that prepare first reads the existing
`r1_ppg_irq_device` cell at `0x200076d0` and invokes slot 08. It then reads the
callback word at `0x200076d4`. If zero, it returns the open status. Otherwise,
it reloads the IRQ handle and dispatches slot 20 with argument words one and
the captured callback, returning that operation's status. Null-device and
missing-operation behavior comes from the existing stock registry providers.
The source uses fresh volatile loads in this order, so an open callback can
change the callback word and/or replace the IRQ handle.

The IRQ handle remains owned and populated by `native_peripheral_bindings.c`.
The previously unowned callback word now has one dedicated source owner,
`r1_goodix_irq_callback`, in `.r1.goodix.irq.callback`. A final source linker
must place it at `0x200076d4`. This reconstruction does not infer its producer
or a function-pointer signature; the native path forwards the word unchanged.

The ignored probe `build/goal-r1-goodix-irq/verify.py` passes 2,592 paired cases
(5,184 executions), executing actual native and reconstructed registry
dispatchers. Final device operations are modeled. Cases cross both entries,
null/A/B device handles, all presence masks for operations 08/0c/20, three
callback words, callback updates to a new value or zero during open, handle
updates to another device or null, and open success/error. Comparison includes
ordered shared-cell reads, operation arguments, final shared state, R0 return
status, stack restoration, preserved registers and interrupt masks.

A deliberate negative source variant reads the callback before opening. The
verifier rejects it when the initial callback is zero and the open operation
sets a nonzero callback: stock binds it while the variant skips binding.
The updated module also passes the existing 630 I2C transport cases and 1,536
binding/transport/reset/close sequences against the current objects.

The full R1 build `build/sources-goal-r1-goodix-irq/report.json` compiles
564 units without failures or duplicate strong symbols. Imports remain
210 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-irq-c-binding-review.json) records the REA snapshot,
source, verifier, report, regression and manifest hashes.

Physical IRQ/GPIOTE behavior, electrical operation, concurrency, invalid
device/table pointer fault paths, callback production, final placement and
byte identity remain unproven. The canonical source plan is unchanged and
G2 workflow gates were not advanced.
