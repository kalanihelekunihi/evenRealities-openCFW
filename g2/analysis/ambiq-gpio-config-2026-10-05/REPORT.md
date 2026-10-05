# GPIO configuration foundation: source, consumer and MMIO contract

This batch implements two previously unverified stock GPIO bodies using unchanged pinned Ambiq SDK5.1.0 source: configuration getter at0x480eee (30 bytes) and setter at0x480f0c (126 bytes). A separate callable O2 source module and reusable four-byte ABI header live in `g2/components/foundation/ambiq_gpio_config`. Its only external executable dependency is the actual shared PRIMASK helper. No scheduler body, old verifier, emulator, shared campaign gate or protected firmware source was changed.

The ranked foundation map recommends matching Ambiq GPIO leaves before board IRQ/DMA/cache glue. Existing GPIO source covered interrupt status/clear/registration/service, not pad configuration. `g2/symbols/apollo_main.tsv` marked both new bodies unverified. Exact original body hashes and direct consumers are retained in `original/evidence.json`; the map itself is preserved rather than edited to imply broader coverage.

## What the functions do

The getter validates logical pin index<224, then nonnull caller output, reads one volatile PINCFG word at0x40010000+4*pin, and writes it to caller-owned output. Returns are0 success,5 invalid pin,6 valid pin with null output. Invalid pin takes precedence over null output. It does not mask interrupts or create a stable snapshot of other pins.

The setter validates the same logical range. Two authenticated seven-word bitmap tables identify extended-drive pads and normal pads supporting additional drive strength. Their values match the pinned public source exactly. For normal pads, only the low two drive bits at10–11 are compared: values2/3 require capability; bit12 is left as the upstream slew field. Extended-drive pads accept pull codes0/1/6 and reject the remaining codes; drive values are not separately rejected in that branch. Other raw configuration bits are not normalized or checked by this function.

Every successful write executes this observable sequence:

```text
save PRIMASK -> CPSID i
write PADKEY 0x40010400 = 0x73
write PINCFG[pin]       = complete raw configuration word
write PADKEY           = 0
restore incoming PRIMASK
```

The key is cleared, not restored to its earlier value. Rejected inputs return5 or7 with no MMIO. The224-index bound is a logical register contract, not proof of224 physical pads. Sparse bitmap holes matter: pin106 is excluded from the extended-drive table despite neighboring pins being included. Use exact bitmap evidence rather than treating comments as contiguous capability ranges.

Readable reconstruction and layouts are in `pseudocode.md`, `gpio_config.h`, and `gpio_config_compat.h`. The compiled C retains the two upstream function bodies byte-for-byte as text. Table bounds are explicitly seven words; table values remain unchanged. `SOURCE_PROVENANCE.json` binds public commit5efc0228528a8adce5eae0d226fac85d2551eb3b, original source hash, unchanged excerpts, pinned type and retained BSD-3-Clause notices. This is verified reuse of selected bodies, not whole-driver or original-compiler attribution.

## Real firmware consumers and practical implications

The radio shutdown routine0x4b49ce calls helper0x52dd7c. That helper clears an output for pin93 through the still-unimplemented state-write family, then calls the new setter at0x52dd8e for pin138 with raw0x3 from0x78ee48. The raw word is recovered; no electrical meaning or complete shutdown safety is inferred from this call alone.

The display power helper0x592c78, whose existing semantic name is inferred `jbd4010_configure_gpio_pins`, calls configuration for pin143 when revision<3, pin128 when revision<4, and pin142 unconditionally. All receive raw0x183 from0x78ee40. The product-revision lookup and complete power-on/off wrappers are outside the implemented source. This is useful for board-specific display features: preserve revision selection and the complete raw word rather than assuming one GPIO layout for all products.

The flash-associated setup function0x46fb0c calls the getter at0x46fd10 with pin103 and a stack-local output before MSPI operations. This is concrete caller/data flow; its MX25U25643G module association remains at the existing unverified confidence. Recovering how that saved configuration is subsequently restored is separate work.

The new interface therefore exposes configuration access needed by real radio/display/flash consumers. It does not supply GPIO output transitions, clocks, NVIC setup, power delays, DMA coherence, or complete board initialization. Caller bodies were examined statically and are excluded from new executed source-comparison coverage.

## Build and fresh validation

`make -C g2 ambiq-gpio-config-simulator` compiles and links the two bodies with the real PRIMASK provider. `ambiq-gpio-config-simulator-test` runs the verifier; `foundation-test` includes the new tests through its Ambiq wildcard, and `CORE_TESTS` includes the new module. Prior targets and their flags are preserved. The Cortex-M4-compatible Thumb2 build is a callable semantic profile for the supported instruction subset, not a claim that the locked Apollo Cortex-M55 firmware uses that compiler or link layout.

The final `comparison-reviewed.json` passes **9,304 fresh stock/source/independent-model cases**. Cases cover every logical pin0–223, invalid224/225/255/U32MAX, prior masks0/1, null/non-null getter outputs, all drive and pull values per pin separately, cross-products over capability classes and sparse boundaries, exact authenticated radio/display constants, and reserved/raw-bit stress. Every accepted setter is checked for exactly three ordered MMIO writes and PRIMASK1 at each access. Getter read/output writes, rejected-input absence of MMIO, final mask, all register cells, output guards, stack and R4–R11 are also checked. No external call is stubbed.

Memory hooks remain installed for MMIO read/write and output-write evidence. Ordinary unrelated RAM reads need no hook in this component. Each case starts a fresh emulator and makes one bounded call; the affected repeated tick/list-insertion pattern is not a dependency. Final-state/model checks supplement, rather than replace, ordered MMIO evidence.

All156 declared stock function bytes execute, plus eight already-counted critical-helper bytes:164 unique original bytes in this profile. There are no newly claimed exact compiled body matches. The unchanged previous59 foundation C/header hashes remain intact; the new component adds three C/header files, for62 total. File counts are navigation facts, not firmware completeness.

Four new unittest methods pass; the fresh affected Ambiq suite passes19 methods. The fresh aggregate completes42 modules:219 executed method tests =213 passing +6 method skips; one setup skip is separate, for7 skip records. There are zero failures/errors. The offline font skip environment is preserved in the aggregate log; no prior successful counts are substituted for the fresh run.

Independent review, including a fresh representative stock/source/model execution with the same MMIO hooks, is retained in `review/report.md` and `review/review.json`. Source/build/comparison hashes are in `build-provenance.json`; exact result counts and limits are in `validation-summary.json`.

## Remaining coverage and next milestone

Deduplicating payload+runtime byte address and verifying identical overlaps adds156 bytes to the foundation source-comparison ledger: **4,166 -> 4,322**, comprising234 touch and4,088 Apollo bytes. Shared PRIMASK bytes are not counted twice. This is bounded executed-source evidence, not newly discovered whole-corpus coverage. Static consumer bodies, table data and failed optimized tick diagnostics add no execution-credit bytes.

Zero of the six locked payloads is demonstrated source-complete, and no source-built byte-identical bundle is established. Whole-image percentages were not remeasured. Both new function bodies have complete declared-byte execution in this test scope, but physical pin function selection, board power ordering, asynchronous behavior and full firmware behavior remain unknown.

Full O2 tick validation remains explicitly blocked by the independently reproduced Unicorn memory-hook limitation. Its failed artifacts remain preserved, and its assertions were not weakened. The GPIO comparison does not clear that gate.

The next useful bounded milestone is the stock GPIO state-write family at0x480fd6 plus the radio helper's pin93-clear/pin138-config chain. That would connect configuration to an actual output transition and remove the currently explicit source boundary in the radio shutdown helper while retaining raw MMIO ordering. It would still require separate hardware/lifecycle evidence before making a shutdown-safety claim.

No commits, staging, flashing, deployment, device access, emulator changes or issue publication occurred. Protected packer, manifest, workflow state and locked firmware identities remain unchanged.
