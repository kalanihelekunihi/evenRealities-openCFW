# Apollo `0x5Dxxxx` none-group source attribution: batch 3

Status: research-only, software-only, not production-routed.

Batch 3 resolves 16 additional census bodies / 3,606 bytes.  The first seven
complete the compiled `pshinter/pshalgo.c` sequence from strong-point
selection through the public `ps_hints_apply` orchestration routine.  The
next nine are source-ordered `pshinter/pshglob.c` bodies for global widths,
blue-zone construction/scaling/snapping, destruction, scale updates, and the
three-function provider table.

Positive evidence includes full source order and call closure, 40-byte point
and 204-byte dimension strides, the 16-entry on-stack strong-point array, the
BlueScale `125/8` overflow-safe comparison, four-zone iteration, `128` width
coalescing, and the final initializer's exact create/set-scale/destroy pointer
order.  Both upstream files and the secondary authenticated decompiler log
used for the 20-byte initializer are content-pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 170 | 29,530 |
| Exact source recovered in batch 3 | 16 | 3,606 |
| Cumulative none-group source | 44 | 7,720 |
| Typed external remainder | 154 | 25,924 |

There is a 320-byte image interval at `0x005D8908`–`0x005D8A48` between
`psh_globals_destroy` and `psh_globals_set_scale`.  It is not represented in
the none-function census.  Source order and the provider table make
`psh_globals_new` a strong candidate, but this batch deliberately records the
interval as an unclaimed typed external until a complete authenticated body
can establish its semantics.  Its bytes and SHA-256 are deterministic in the
analyzer, preventing it from becoming an invisible gap.

FreeType implementation source retains the FreeType Project License.  The
Apache-2.0 research adapter copies no implementation.  No production
component, global census, manifest, package, overlay, Makefile, or hardware
path is modified.
