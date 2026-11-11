# Flash-read and FAL save-frame fidelity

The prior partial-read counterexample now matches stock in 1,920 strict
native-chain comparisons at controlled read-adapter placement. The repair
keeps both policies in C: empty register-liveness constraints cause the
compiler to preserve the native frames, without adding hand-written machine
instructions or initializing unavailable flash bytes.

The read adapter at `0x3f03e` now retains live R4/R5/R6 and saves those three
registers plus LR, matching the native 16-byte frame. FAL read retains R8/R9/R10
across its C body, producing the native eight-word R4–R10/LR save frame.
That frame becomes the future raw TSL buffer during sector header reads.
Its contents must survive failed or non-writing driver calls.

Placement also matters. A dedicated function section with two-byte alignment
allows the adapter entry at `0x3f03e` and its FAL-call return word at `0x3f051`.
Default four-byte alignment had shifted the function by two bytes, changing
that saved word. The controlled linker verifies the exact entry; it does not
replace saved addresses with normalized values. Normal source-plan admission
still requires instruction qualification.

REA observes the adapter's complete 28-byte stock body through `0x3f059`.
The locked application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

[Machine-readable evidence](flash-read-frame-review.json) binds:

- 1,920 strict stock/C sector-to-FAL cases. They match results, calls, tracked
  shared-access order, outer frame, nested raw bytes and partition snapshots.
  Actual C sector, adapter, TSL/status, FAL partition and cache code execute.
  The final flash driver, printf and path getter are modeled. The earlier
  native counterexample disappears in this fixture set.
- 9,310 read/status/TSL comparisons and 12,302 sector comparisons pass again.
  The sector group still distinguishes 240 bounded 16-read prefixes from
  completed return/assertion cases.
- 9,216 FAL-read comparisons and 6,144 FAL/cache integration comparisons pass.
  Restoring the old FAL save frame or shifting the adapter entry by two bytes
  makes the strict native-chain comparison fail again.
- Only the expected two compilation objects change; the other 573 are byte
  unchanged. Mutable/readonly data owners, manifest, aliases and composed
  import sets remain unchanged. Neighboring status-scanner code has compiler
  layout differences and is covered by its regression matrix.

All 575 R1 units compile without failures or duplicate strong symbols; imports
remain 175 application and 34 bootloader. `make sources-check` passes. Ten
qualification variants compile, with no exact region selected. The C adapter
still uses IT MI where stock uses BGE, so this is not instruction identity.
The scoped qualification wrapper resolves the generated FAL input to its
materialized path after selecting manifest anchors; the generic qualifier
otherwise leaves `{gen}` unresolved. Equality checks are unchanged.
The later [generated-input repair](generated-qualification-review.md) removes
that generic qualifier limitation; the scoped wrapper above records the prior run.
The canonical plan remains at 3,881 source-built application bytes, 642,279
binary pull-through bytes and 248 resource bytes. The hybrid application
equals stock with source completeness explicitly false.

These results depend on the controlled native adapter address and current
compiler's verified frame layout. They do not establish arbitrary relocated
execution, real flash hardware, startup, concurrency, unused register/flag
values, every private frame, complete source linking or a byte-identical full
source rebuild. No G2 gate advances; the overall goal remains active.
