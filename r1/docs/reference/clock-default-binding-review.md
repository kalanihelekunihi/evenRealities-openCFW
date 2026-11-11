# Default RTC backend binding and exact callbacks

Current status: [bootstrap normal-link integration](clock-bootstrap-link-review.md) closes the later callback gate; the results below retain their original scope.

The native getter at `0x5a988` returns the eight-word table at `0x99c8c`. REA byte reads and independent Thumb decoding establish its callback roles:

| Slot | Native entry | C role |
| --- | --- | --- |
| 0 | `0x50d86` | `default_init`, return 1 |
| 4 | `0x50d60` | `default_deinit`, return 1 |
| 8 | `0x50d7e` | `default_get`, tail branch to `0x514bc` |
| 12 | `0x50d82` | `default_read64`, tail branch to `0x51494` |
| 16 | `0x50db6` | `r1_clock_backend_update` |
| 20 | `0x50d64` | calendar read provider, still external in C |
| 24 | `0x50d8a` | calendar write provider, still external in C |
| 28 | `0x50daa` | `r1_clock_backend_bind_tick` |

The C table in `r1/src/application/board/native_clock_bootstrap.c` now points slot 12 at a separate C tail veneer, matching stock's call graph. It previously pointed directly at the underlying sixty-four-bit request. The new veneer adds no stack frame and retains the complete R0/R1 result. This confirms the backend association deferred in the [read-request review](clock-read64-frame-review.md).

The official qualifier accepts **five new regions totaling 24 bytes**: four four-byte callbacks and the eight-byte getter. The getter includes four instruction bytes and its four-byte table-address literal. The generic qualification scope includes bootstrap, clock-port and structured-time units so pure tail veneers can bind their independently named callees. Fifteen generic and twelve GCC9 variants compile. Generic qualification admits all five regions; GCC9 independently accepts the four callback fragments. Existing qualified regions are not counted again.

Two qualifier-generated units are appended to the canonical source plan without changing earlier units. The table itself remains retained stock data; its symbolic C initializer is not admitted as an exact data region by this work. Getter relocation binds the native table address, and tail relocations bind the recovered native request entries. These selected fragments do not establish a complete C table placement or full source link.

The normal Clang object passes **240 paired cases / 480 executions** covering the getter and four callbacks. Checks verify the returned table pointer and all eight source/native callback roles, zero-stack tail entry into the modeled epoch/sixty-four-bit request helpers, full-width return values, every R0-R12 value and APSR on return, active R4-R11, final SP and interrupt masks. Code/table addresses are normalized by verified role; LR return-address bits are excluded. Negative controls reject the wrong sixty-four-bit delegate and the wrong deinitialization status.

All 576 R1 units compile and compose without new failures or duplicate strong symbols. All 575 other objects and all eight previous bootstrap function bodies and relocations are unchanged. Only table slot 12 changes its relocation; the other seven entries remain unchanged. Imports remain 164 application / 34 bootloader. No assembly is added.

The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. It now has **4,023 source-built bytes**, 642,137 fallback bytes and 248 resource bytes. Source-built totals include assembly and data. Physical RTC operation, complete calendar-provider closure, final C table placement and source completeness remain unproven.

REA read the getter's eight-byte envelope, the complete thirty-two-byte native table and the forty-two-byte code window containing the small callbacks and calendar-read provider. Only the five qualifier-selected regions enter the source plan. Evidence: [clock-default-binding-review.json](clock-default-binding-review.json). Local probes and qualification receipts are under ignored `build/goal-r1-clock-default-binding/`; normal report `build/sources-goal-r1-clock-default-binding/report.json`, hybrid report `build/hybrid-goal-r1-clock-default-binding/build-report.json`.

The subsequent [calendar provider composition review](clock-calendar-composition-review.md) validates and enables the calendar ports, selected inverse converter and RTC request unit in normal composition. Bootstrap initialization remains compile-only.
