# KV initialization bound to the existing FAL state query

`r1_kv_port_initialize` now calls the pinned FAL C function `fal_init_check`
instead of the unresolved reconstruction name `r1_fal_is_initialized`. No
second getter, state byte or success stub was added. The source declaration
uses the provider's `int` return type; the observed byte values are 0..255.

The locked KV initializer at `0x94e3c` calls the flag reader `0x62fe8` at
`0x94e4c`, branches over `fal_init` for a nonzero result, then continues with
partition lookup. Raw instructions and REA establish that `0x62fe8` returns
the byte at `0x200077b1`. The same byte is written by stock `fal_init` at
`0x62f40`: flash/partition failure clears it; first successful initialization
sets it to one. The pinned FAL source's private `init_ok` and `fal_init_check`
carry this state relationship, so the KV client now consumes that existing
owner rather than introducing another representation.

`build/goal-r1-fal-init-query/verify.py` passes 288 paired cases. It checks all
256 byte values through the stock and C getters, including the exact single
byte read, R0 zero extension, untouched surrounding memory, stack restoration,
preserved registers, flags and interrupt masks. Another 32 cases cross native
initial flag states zero/one with flash and partition success/failure results.
They execute native/C initialization and then the real getter, checking result
words, provider-call ordering and the shared state subsequently observed.
Flash/partition operations and native diagnostics are modeled boundaries.

The initialization checks do not prove full `fal_init` instruction or logging
equivalence. The existing generic FAL diagnostic configuration remains separate
debt; printf effects and arbitrary external writes to nonboolean init state
are outside this comparison. The getter itself is checked for every byte.

The full build `build/sources-goal-r1-fal-init-query/report.json` compiles all
567 R1 units without failures or duplicate strong symbols. Application imports
fall from 202 to 201, removing only `r1_fal_is_initialized`; bootloader imports
remain 34. `make sources-check` passes. The newly anchored getter was also
tested by the official qualifier with recorded and Oz compiler options; neither
variant selected an exact region. The canonical source plan is unchanged.
[Machine evidence](fal-init-query-c-binding-review.json) binds REA, compiler
and execution inputs, qualifier results and the normal build report by hash.

Physical flash initialization, complete FAL behavior, final linking/placement,
byte identity and source completeness remain unproven. G2 workflow gates are
unchanged.
