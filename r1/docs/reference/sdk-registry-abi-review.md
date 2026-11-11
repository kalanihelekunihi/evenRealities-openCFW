# Shared SDK observer iterator ABI repair

The normal composition's shared `nrf_section_iter.c` implementation uses the
recovered multi-range ABI, as does the BLE poller. However, the participating
`nrf_sdh.c`, `nrf_sdh_soc.c` and `nrf_pwr_mgmt.c` units still compiled the SDK's
GNU single-range types. Their descriptors and cursor reads were incompatible
with the shared implementation. Linking boundary names alone would not fix it.

Those three units now include `section_users_contract.h`, which selects the
existing `section_legacy_abi.h` and checks configured range counts. The SDK
sources remain unchanged. `native_sdk_observers.ld` supplies section-relative
start/stop symbols for the existing request, state, stack, SoC and power
priorities. It retains their existing records and asserts whole record widths.
The prior BLE layout remains selected independently.

The SDK configuration has two priorities for each SoftDevice set and three
for power handlers. Three is a candidate configuration value, not a recovered
stock handler inventory. There are currently no registered power handlers;
the linker leaves those ranges empty. No handlers are fabricated. Existing
product-specific observer owners excluded from normal composition remain
excluded.

The SoC priority-zero layout explicitly places the clock object before
fstorage. REA confirms stock records for clock, fstorage and DFU at
`0xc45d0..0xc45e8`, with handlers `0x907fd`, `0x78d09`, `0x52279` and null
contexts. The composed relocation order and linked probe both check that
clock precedes fstorage. A defective layout with ordinary input order links
successfully but fails the observer-order assertion.

A controlled replay links the old GNU `nrf_sdh.c` user against the actual
shared legacy iterator, supplying valid GNU boundary aliases. The state
notifier repeatedly calls the first observer instead of advancing. The
probe stops after its third repeated call; two source-owned records were
expected. The repaired user advances through both records.

The normal probe links ten actual source objects and places priority ranges
separately before final relocation. It passes forty iterator-mask cases
across all six descriptor sets, forty real request/state notifier scenarios,
and thirty-six integrated stack-poll workflows. The latter execute the
actual stack dispatcher, BLE and SoC pollers, descriptors and iterator for
zero through three events per queue, both suspend-state byte values and
both PRIMASK settings. Direct `nrf_sdh_evts_poll` has no suspend gate; the
fixture follows that source behavior. SVC97 BLE retrieval, SVC75 SoC
retrieval and leaf callbacks are modeled. Caller-clobbered integer registers
are poisoned at modeled callbacks. Provider order, contexts, request busy
status, event values, SP, callee-saved registers and masks are checked.
Power verification covers only its empty descriptor/iterator contract.

All 802 R1 units compile without failures or duplicate strong symbols.
Application imports decrease from 83 to 73, removing exactly ten registry
names with no new imports. The three SDK sources and their public definition
sets are unchanged; their compiled cursor/descriptor accesses now agree.
All 797 other prior object hashes are unchanged. Two generated boot objects
retain source hashes, allocated bytes and relocations. Existing BLE registry
bytes/relocations are unchanged, including single DFU registration. Strict
bootloader linking and R1 source checks pass. The global check retains the
unrelated unlisted G2 `resident_rom_thumb_set.S` failure.

Physical radio/flash/power behavior, complete initialization, asynchronous
operation, excluded product observers, power shutdown handlers and full
application final linking remain unfinished. No source-plan selections
change. The [machine-readable review](sdk-registry-abi-review.json) binds
source, layout, REA, build, old-failure and repaired-execution evidence.
