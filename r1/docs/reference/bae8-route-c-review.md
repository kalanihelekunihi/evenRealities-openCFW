# R1 BAE8 event router and timeout callback in C

`native_bae8_route.c` implements the router at application `0x5d5e0` (418
stock code bytes) and the return-only timeout callback at `0x4d2f0` (two bytes).
Startup now resolves its event-route symbol to this C unit. The router is a
bounded C behavior candidate with a retained frame counterexample. Only the
two-byte timeout callback enters the canonical exact source plan.

## Dispatch and corrected dependency identity

Type 2 selects the factory receive encoder only when the full configuration
getter result equals 85; otherwise it uses the BC receive queue. Both receive
connection, channel 1, payload pointer and 16-bit length. Type 3 first cancels
the timeout callback with argument zero, then invokes EUS reassembly on channel
2. Nonzero receive results retain the native logging behavior.

Types 6/7 assign the glasses connection role before looking up link context;
types 8/9 only perform the lookup. Lookup failures are logged. On success the
router reports the current BC or EUS notification byte according to the log
mode. Other event types do nothing. Field reloads and provider-query order
follow stock, including mutations during role assignment, cancellation and
logging. No new handwritten assembly is introduced.

The old frontier called both `0x33dbc` and `0x33850`
`r1_ble_thread_message_encode`. They are different functions: the router's
`0x33dbc` call places payload in R2 and length in R3; the existing C encoder
at `0x33850` takes length in R2 and payload in R3. The unresolved `0x33dbc`
candidate is now named `r1_bae8_bc_rx_enqueue`. Its legacy source label is
retained as history; the router does not bind to the incompatible encoder.

## Runtime proof and retained frame gap

The replay executes actual C startup to install the callback, then invokes
that installed pointer. In 6,522 paired cases, native/C dispatch, arguments,
log contents, context outputs, bounded RAM accesses and final state match.
Cases cover every byte-sized event type, valid/invalid connections, full-word
factory selectors and receive statuses, basic and changing full-word log modes,
both PRIMASK states, and mutations of event fields, context descriptors and
notification bytes.

The real native/C context helper and SDK connection-index/validity functions
execute. The output slot is not retained or forwarded by that helper: the
stock body writes the output word and passes only the connection to its index
callee. Replay watches both output writes and all relevant descriptor/pool
accesses. With the validated non-overlapping service, descriptor and pool
objects, only the private output-slot address is normalized. Payload pointers,
returned client pointers and other data addresses are compared directly.

The native router has a 40-byte frame and output at caller SP minus 36. Current
Clang C has a 32-byte frame and output at minus 24; its final std1 calls can be
zero-frame tails. The strict native-frame replay rejects this C layout, and
the counterexample is retained. Provider depths are recorded rather than
equated. This is not whole-route frame, byte or physical equivalence. Lower
queue/reassembly and role-assignment bodies remain unresolved, so hidden
dependencies on their deeper stack layouts are not ruled out.

Payload queues, factory getter, role assignment, cancellation, log providers
and connection flags are modeled. Internal nonargument registers, APSR, private
spills and timing are excluded for the router. Five negative controls reject
factory-selector truncation, wrong BC channel, omitted cancellation, wrong
notification byte and inverted receive-error handling. Interrupt scheduling,
live RTOS behavior, complete startup and physical BLE are unvalidated.

The timeout leaf separately passes 2,072 paired cases preserving all integer
registers, SP/LR, APSR and interrupt masks. Its C body compiles to the exact
two stock bytes. REA windows for both native entries match the locked image.

## Build and exact admission

`build/sources-goal-r1-bae8-route-c/report.json` compiles all 597 units
(523 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols; all previous 596 objects are unchanged.
`make sources-check` passes with 401 R1 source files. One import is resolved
and four deeper imports become explicit, so application imports rise from
155 to 158; bootloader imports remain 34. The new unresolved bodies are:

- `r1_bae8_bc_rx_enqueue` at `0x33dbc`;
- `r1_factory_thread_message_encode` at `0x33af8`;
- `r1_eus_rx_reassembly` at `0x32198`;
- `r1_glasses_connection_role_assign` at `0x4d654`.

The later [role-policy review](glasses-role-c-review.md) supplies the last
provider's C policy and diagnostics, retaining its fault-transition dependency.

Qualification selects only `r1_bae8_rx_timeout_noop` at `0x4d2f0..0x4d2f2`.
Its qualifier-produced region was merged without overlap, preview-built, and
promoted after checking the actual source owner and whole application equality.
All previous source-plan units are retained. Totals become 4,271 source-built,
641,889 binary-pull-through and 248 resource bytes. The application remains
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The router contributes zero exact bytes. Complete source firmware remains
unproven; the unchanged hybrid hash still depends heavily on stock code.

The [receipt](bae8-route-c-review.json) records source/object identity, REA,
runtime checks, negative controls, the strict frame rejection and exact
admission audit. Probes are under ignored `build/goal-r1-bae8-route-c/`.
