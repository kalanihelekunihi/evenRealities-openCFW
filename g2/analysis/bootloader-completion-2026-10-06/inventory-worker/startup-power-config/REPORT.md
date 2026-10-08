# Startup power configuration, callbacks and temperature response

Independent reconstruction of locked bootloader SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, Thumb little-endian, load `0x410000`. Source is `g2/components/bootloader/initializer_callbacks/startup_power_config.c/.h`. No retained executable blob or stock fallback in the source machine.

Eight bodies / 564 original instruction bytes are visited by 697 stock-versus-source comparisons on candidate `761be470`. Addresses: configure `41c86c..41c986`, temperature `41ca2c..41ca5c`, sink setter `41583c..415844`, register setup `41c7de..41c834`, readiness `41bf3a..41bf84`, hooks `41cd76..41cd8c`, `41cd8c..41cda2`, `41cda2..41cdb8`. [Receipt](comparison.json), [coverage](function-coverage.json), [runner](verify.py).

## Configuration call chain

Only the low byte of the operation selects behavior; unsupported values return 6. Operation 0 returns immediately when `40021108[5:4]==3`; otherwise calls before hook, performs ten ordered volatile register updates, sets `40020378` bit31 and `4002033c` low four bits, calls middle hook, sets `40021100` bit0 and calls after hook. Hook statuses are ignored. Hooks read callback slots `20026e4c/50/54`; absent hooks return zero.

Operation 1 queries native descriptor selector23, whose mask is `00200000` (not selector25's `00800000`). An inactive resource returns zero. An active resource first runs readiness then native power-leave23, propagating either failure. Readiness checks `40020180` mask100 with a 100-delay-call bound; failure checks `400c0a7c` bit0, sets `400c0a80` bit0 and retries primary readiness. Delay-call counts have no proven millisecond unit.

Operation 2 replaces `40020124` bits2..7 with value32 and writes 1 to `40020120`. Operation 3 clears DEMCR bit24 and `40020250` bits0..3, zeroes whole words `40021004/0c`, polls masks `3fffffff/4c4` with bound5 and invokes callback operations3/4 with an initially zero response word. Poll failures propagate; callback statuses are ignored.

## Temperature interface and ownership

The stock float input is in S0. Its synchronous 12-byte borrowed stack packet is `{input_float_bits, incoming_R1, incoming_R2}` and is passed to native power callback operation2, flag0. Callback success copies the last two words to the caller's eight-byte output. Absent callbacks return success without writing the packet, so zero status does not establish a valid temperature reading. Partial callbacks preserve the untouched incoming register word. A callback error zeroes both output words and returns 1. Physical units of either response word remain unresolved.

The reconstructed naked assembly retains this concrete ABI without undefined uninitialized C reads. There is no allocation, retained pointer or asynchronous lifetime claim. The misleading external-mode setter name is retained for compatibility: `41583c` merely writes the plain logger sink callback at `200270cc`; it does not change a hardware mode.

## Validation and limits

Tests compare ordered MMIO writes, return values, IRQ state, callback payloads and output bytes. Native query/power/critical/wait helpers execute; elapsed delays, registered callback bodies and peripheral acknowledgement are controlled. No SRAM write hook is installed. Initial insufficient selector fixture evidence is preserved separately; correcting the selector23 mask exposes the full active-resource branch. A wrong source variant that propagates the operation0 after-hook error is rejected (stock0 versus mutant7); production source is unchanged by that control.

Synthetic readiness and acknowledgement do not establish real hardware timing, scheduler quiescence, IRQ/task drain or physical temperature semantics. Seven integration cases retain preexisting startup/logger models; direct tests establish these newly reconstructed bodies separately. Source completeness, producing compiler compatibility and byte identity are not claimed.

## Promotion

Checkpoint761be47077105549cc3ae0688ec5b27b3c850bf49b51011135e8f76192ddbd30 promoted after all7 cases PASS,26 direct/regression receipts PASS,670 files/172 objects unchanged with exact frozen copies authenticated,493 mappings PASS and zero manifest mismatches. Prior64e52504/4edd remain preserved. Selected OTA entries13→10, same address-based scope; no new aliases. Seven-case observed instruction footprint remains38764/148599, not source-completeness or native integration coverage for these modeled startup bodies.
