# Goodix accelerometer start/stop HAL C binding

The selected HAL now reaches the native board callback policy. `hal_gsensor_start_cache_data` aliases the new C `r1_goodix_gsensor_cache_commit` body for stock `0x6f964..0x6f99f`. `hal_gsensor_stop_cache_data` aliases the already checked C stop body at `0x6f9d4`. The two superseded template definitions are omitted from the generated demo-user unit. Each alias shares its implementation's address; there is no forwarding copy or executable inline assembly.

REA observes the start sequence: sample the formatting pointer at `0x20007b04`; if present, clear 180 scratch bytes and format the stock message; sample the print pointer at `0x20007b00` and call it if present; call timestamp initialization; then load the live start slot at `0x2002fd28` and tail-call it if nonnull. Later callback pointers can change during earlier callbacks, so they are not cached early. The stock message ends in actual CR/LF bytes.

The C body reserves 184 scratch bytes and uses the return value of the existing opaque `memset` provider to pass the cleared buffer to formatting. Under the recorded Clang profile, this emits the native R4/LR save pair and a total 192-byte frame; the first 180 bytes are cleared and four padding bytes are retained. `musttail` restores the caller frame before the board callback. This frame evidence is compiler/profile-specific, not a portable ISO C stack-layout guarantee.

Verification against `build/sources-goal-r1-goodix-cache-start-final/report.json`:

- 384 paired stock/C start cases cover optional loggers/start callback, callback replacement/removal, return-bit patterns and caller clobbers, interrupt masks, retained frame bytes and scratch/callback-table alias fixtures. Timestamp initialization executes the actual stock/C no-work bodies. Clear, formatting, printing and board callbacks are modeled; native memclr and C memset are compared as the same zero operation with different provider ABIs. Message contents, rather than source literal addresses, are compared.
- 32 paired stop cases execute the exported HAL alias and check the live stop slot, null handling, callback mutation, caller-SP tail transfer, saved registers and masks. The stop callback is modeled.
- Wrong clear length (184 rather than 180) and wrong callback slot are rejected. An initial escaped-string mismatch was caught and corrected before final verification.
- All 576 units compile without failures or duplicate strong symbols; unresolved import sets stay 168/34. All 574 unrelated objects, the three existing callback functions and 19 retained demo-user function bodies are byte unchanged. Profiles and unit counts stay unchanged.

Five official qualification profiles compile but select no regions. The new C start body differs from stock instructions, so the canonical source plan is unchanged. Its hybrid image still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,945 source-built bytes, 642,215 fallback bytes and 248 resource bytes. Real formatting, physical sampling and concurrent callback changes remain unverified; full firmware source completeness and G2 gates remain unproven.

[Machine-readable evidence](goodix-cache-start-c-binding-review.json) binds REA, source/generator ownership, behavior and negative probes, object audit, qualification and canonical hybrid. Probes remain under ignored `build/goal-r1-goodix-cache-start/`.
