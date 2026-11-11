# Relocatable BLE observer registry boundaries

Normal source composition now applies
`src/config/runtime/native_ble_observers.ld`. It defines the start and stop
symbols for BLE observer priorities zero through three around the existing
C-owned sections. Each symbol is section-relative, so a later firmware link
can move the ranges without stock address aliases. The script retains each
range and asserts whole eight-byte handler/context records. No observer is
added or copied.

The four ranges contain 1, 5, 5 and 1 records. REA confirms the complete
96-byte stock inventory at `0xc4568..0xc45c8`. A linked fixture places the
ranges separately at `0x1010000`, `0x1010100`, `0x1010200` and `0x1010300`.
Its tables match stock after normalizing the relocated priority-zero callback
code address. All eight boundaries relocate to the correct section ends.
The existing duplicate DFU registration fix is preserved.

The fixture links the actual normal-build Nordic BLE event poller, its
four-range descriptors, the legacy SDK iterator, the native observer tables
and the SDK priority-zero registration. Forty-eight poll scenarios exercise
stack-enabled gating, zero through four queued events, both PRIMASK settings,
normal queue exhaustion and unexpected full-width error codes. All twelve
handlers receive each event in priority order with the correct context; the
error adapter receives unexpected statuses. SVC97 event retrieval and
observer callbacks are modeled. The enabled-state byte is seeded, rather
than initialized through a real SoftDevice.

Direct execution of the same iterator also passes all sixteen combinations
of empty/nonempty priority ranges. Two defective layouts link successfully
but fail boundary assertions: skipping priority one's first record and
omitting priority two's last record. The normal probe is rerun afterward.

All 802 R1 units compile with no failures or duplicate strong symbols.
Application imports decrease from 91 to 83, removing exactly the eight BLE
boundary names. All composed allocated bytes and normalized relocations
are unchanged. All 800 nongenerated prior object hashes are unchanged;
two generated boot objects retain allocated bytes and relocation identities.
The only manifest change selects the BLE layout for application composition.
Strict bootloader linking and R1 source checks pass. Global source checking
still fails on the unrelated unlisted G2 `resident_rom_thumb_set.S`.

This is registry linking within a relocatable composition, not a complete
firmware final link. Other SDK registries, startup integration, physical
radio behavior, asynchronous effects and callback internals remain open.
No source-plan selections change. Exact inputs, tables, symbols and probe
hashes are recorded in [the machine-readable review](ble-registry-link-review.json).
