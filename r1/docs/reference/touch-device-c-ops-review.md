# Touch registry device operations reconstructed in C

Seven native touch wrappers now have one C implementation each in
`native_touch_device_ops.c`, using the existing cached-handle owners in
`native_peripheral_bindings.c`. No new cache storage or inferred context span
is introduced. REA confirms the native cache words at bus `0x200067fc`, output
`0x20006800` and input `0x20006804`.

| Native entry | C symbol | Observed contract |
| --- | --- | --- |
| `0x46f54` | `r1_touch_record_op_0c_b` | Bus slot `0x0c` |
| `0x46f60` | `r1_touch_record_op_08` | Bus slot `0x08` |
| `0x46f6c` | `r1_touch_device_op_stop` | Input slot `0x0c`, reload handle, then slot `0x20` with words one/zero |
| `0x46f88` | `delayed_touch_release` | Tail-call shared-power release with client two |
| `0x46f90` | `r1_touch_record_op_0c` | Output slot `0x0c` |
| `0x46f9c` | `r1_touch_device_op_lock1` | Output slot `0x08`, reload handle, then slot `0x18` with words one/zero |
| `0x46fb8` | `r1_touch_device_op_unlock` | Output slot `0x08`, reload handle, then slot `0x18` with words zero/zero |

The two-stage routines discard the first operation's result and return the
second's raw word. Leaf dispatcher results are also preserved as observed R0
values, without inferring semantic return use from decompiler void annotations.
The power-release wrapper retains its void boundary. Volatile cached pointer
loads prevent a pre-open/close snapshot from replacing the required reload.
Electrical interpretations of the selectors are not assumed from historical
lock/unlock labels.

The execution probe passes 2,016 paired stock/C cases (4,032 executions) with
actual native/C registry dispatch and existing C cache storage. Device methods
and the shared-power release boundary are modeled. Cases vary each wrapper,
null/two handles before and after callbacks, absent/present open/close/word
methods and raw result words. It compares ordered cache reads, method arguments,
result/final-cache state, preserved registers/stack/masks and original caller
SP/LR at tail method entry. Registry null and missing-method policies remain
unchanged. A cached-output-handle negative control fails when open replaces A
with B: stock applies slot `0x18` to B, the variant to A.

The normal report `build/sources-goal-r1-touch-device-ops/report.json` compiles
572 R1 units without failures or duplicate strong symbols. Imports remain
197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](touch-device-c-ops-review.json) binds REA, source, cache and
registry providers, probe, negative control and normal build by hash.

Default C sizes are 14/14/30/6/14/30/30 bytes versus native instruction sizes
8/8/24/6/8/24/24. No byte qualification was performed. The canonical source plan
stays unchanged at 3,821 source-built bytes in the last verified hybrid. Initial
placement, private frames/caller-clobbered registers/flags, concrete method
semantics, concurrency, electrical IRQ/power/timing, complete source-only byte
identity and G2 corpus gates remain unverified.
