# Source-owned flash-storage registry

Normal composition now applies `native_fstorage.ld`. Its writable, aligned
40-byte `.fs_data` section contains the existing
`r1_internal_flash_context` followed by the existing SDK FDS `m_fs`.
Previously those allocations occupied separate sections, and the registry
boundaries were unresolved. The layout defines section-relative start/stop
symbols and asserts whole 20-byte instances. It creates no storage copies.

The internal-flash context must participate in global busy scans. Registering
only the SDK's original `.fs_data` input would omit the device-flash allocation.
The linked fixture checks both owner addresses, order, writable flags and
bounds after relocation. Two layouts that omit device flash or truncate the
scan link successfully but fail registry assertions.

REA confirms the stock busy function at `0x78c80` and its two-instance bounds,
`0x20007dc0..0x20007de8`. Executing the actual stock decompressor authenticates
all 6,492 initialized-data bytes against an independent token decoder and
checks adjacent guards. The first compiled instance matches the corresponding
stock cold bytes at its test binding. The second C instance uses the SDK FDS
callback; its attribution to the second stock instance is unproven. This
review does not claim complete stock registry identity.

The actual source fstorage facade passes 640 stock/C busy comparisons.
Cases cover each instance initialized/uninitialized, global and direct
queries, external instances, valid bool busy results, both PRIMASK settings
and a callback changing the next instance's API before the scan reaches it.
An explicitly uninitialized instance triggers the stock all-instance fallback.
Provider arguments/order, return values, live field changes, SP, callee-saved
registers and interrupt masks are checked.

Another 64 source workflows execute actual initialization, global busy and
uninitialization on each registered allocation. Modeled API initialization
observes the already-installed API pointer. Even a failing initializer leaves
that pointer installed, matching the SDK. Uninitialization clears API/flash
info after its callback even on error, while retaining callback and extent
fields. Actual backend API callbacks are modeled; FDS initialization and
SoftDevice flash requests do not execute in this fixture.

All 802 R1 units compile without failures or duplicate strong symbols.
Application imports decrease from 73 to 71, removing exactly the two registry
boundaries. All 800 nongenerated prior object hashes are unchanged. Two
generated boot objects retain source hashes, allocated bytes and relocations.
The composition audit verifies one merge of the existing records and every
expected twenty-byte FDS section-reference addend rebase. All other composed
bytes and relocations are unchanged. Strict bootloader linking and R1 source
checks pass; the global source check retains the unrelated unlisted G2
`resident_rom_thumb_set.S` failure.

A final application link must place `.fs_data` inside the initialized RAM copy
span. That startup integration, physical flash behavior, actual backend
operation, asynchronous effects, FDS stock identity and full application
linking remain open. No source-plan selections change. Exact inputs and proof
boundaries are in [the machine-readable review](fstorage-registry-review.json).
