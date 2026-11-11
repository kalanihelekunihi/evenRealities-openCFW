# Shared logging module registry

The existing native C module table preserves the 32 IDs used by reconstructed
hardware paths, including `app` at ID 28. Separately collecting the SDK's
28 module records would give those paths a different namespace. Normal
composition now selects `native_log_registry.ld`: it keeps the native table
once and provides section-relative SDK symbol aliases to its existing rows.
Twenty-six duplicate SDK records are discarded. The two additional SDK
modules, `peer_manager_ast` and `sortlist`, retain their own records as IDs
32 and 33. No module names are duplicated in the resulting 34-record table.

Aliases are defined inside the output section. An alias defined as an absolute
number would remain unrelocated in a later firmware link. The probe moves the
table to `0x1080000` and checks every SDK symbol's section and offset. It also
compiles the actual SDK `NRF_LOG_MODULE_ID_GET_CONST` macro and executes it
against all 34 symbols, verifying the resulting IDs after final relocation.
A wrong app-ID alias and an absolute app alias both link but fail assertions.

REA authenticates the 256-byte stock table at `0xc441c`. All 32 native names
and nonpointer record fields agree with stock. Their source records, strings
and relocations are unchanged. The source table now additionally owns 34
four-byte dynamic records with initialized name-order ranks and zero runtime
filters. This supports the SDK's ordered-name queries while runtime filters
are disabled; it is source initialization, not a claimed stock dynamic arena.
Inventory/stride assertions fail if the constant and dynamic module counts
diverge or an unmapped SDK module appears.

The linked actual SDK getters and compiled module-ID macro pass 2,233
executions. They cover every direct and ordered name, all module-ID routes,
all color branches, compiled/runtime-filter query variants, invalid ordered
IDs and both PRIMASK settings. The color cases include 448 stock/C pairs
across the 32 native modules. Returns, SP, callee-saved registers and masks
are checked. The normal probe is rerun after defective aliases.

All 802 R1 units compile without failures or duplicate strong symbols.
Application imports decrease from 71 to 68, removing the constant start/stop
and dynamic start boundaries. All 799 other prior object hashes are unchanged;
two generated boot objects retain source hashes, allocated bytes and
relocations. The composition audit verifies the exact canonical-plus-extra
record merge, all aliases, unchanged existing metadata, and every other
composed byte/relocation. Strict bootloader linking and R1 source checks pass.
Global source checking retains the unrelated unlisted G2
`resident_rom_thumb_set.S` failure.

The dynamic records must be copied into initialized RAM by final startup code.
That placement, logger backend dispatch, rendered messages, physical diagnostic
output and full application final linking remain unverified. No source-plan
selections change. The [machine-readable review](log-registry-review.json)
records the exact source, SDK, layout, REA and execution evidence.
