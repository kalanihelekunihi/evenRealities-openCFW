# Single ownership of the DFU BLE registration

The normal source composition previously contained six priority-2 BLE
observer records. Its reconstructed table supplied the five stock records,
including DFU, while the full SDK `ble_dfu.c` object supplied another DFU
record. A final registry collecting that section would dispatch DFU twice.
The SDK callback ignores its context argument and uses private `m_dfu` state,
so the two different record contexts do not prevent duplicate handling.

`runtime/native_dfu_service.c` now compiles the unchanged pinned SDK service
with its registration macro suppressed. The reconstructed table remains the
sole owner of the stock registration. This follows the existing peer-manager
ownership convention. All four exported service functions, their helpers,
private service state and nonregistration relocations are preserved. The
only removed allocated section is the SDK's eight-byte observer record and
its two relocations. No extra service implementation or state is added.

REA confirms the stock 40-byte priority-2 table at `0xc4598`. Linked probe
images demonstrate the previous 48-byte inventory and the corrected 40-byte
inventory. After normalizing the relocated SDK callback address, all five
canonical records match stock bytes, including order and contexts. Seventy
modeled dispatch scenarios cover seven event IDs, five connection handles
and both PRIMASK values. The previous image dispatches DFU twice; the corrected
image dispatches it once. Other records retain their order and contexts.
Callbacks are modeled at entry; this does not exercise their internals.

All 802 R1 units compile without failures or duplicate strong symbols.
Imports remain 91 application and 22 bootloader linker symbols. The other
799 prior object hashes are unchanged. Two generated boot objects retain
source hashes, allocated bytes and relocation identities. Strict bootloader
linking and R1 source checks pass. The global source check retains the
unrelated G2 unlisted `resident_rom_thumb_set.S` failure. The composition
receipt now derives participating-object counts from actual linked units;
the report's shortened command array is not an object inventory.

SDK section boundaries and complete application final linking remain open.
The canonical record still calls the SDK observer. Wiring the recovered
native observer, its separate context, and SDK initialization into a shared
lifecycle remains separate work; this fix does not claim that integration.
Physical BLE/DFU behavior is unverified. No source-plan selections change.
[The machine-readable receipt](dfu-observer-owner-review.json) binds the
stock bytes, build, dispatch reproduction and section/relocation audit.
