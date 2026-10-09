# Independent flash receipt review — 2026-10-09

## Concrete correction: claimed mismatch is false

The locked stock image really tests original response bit5: 470430 loads the received byte; 470434 is `lsls r0,r0,#26` (raw bytes8006); 470436 branches on positive. This tests 0x20, not0x40. But the official acquired Macronix sample **also tests0x20 for RDCR**. `sample/MX25U25643G_DEF.h:119` defines `FLASH_4BYTE_CF_MASK 0x20`; `MX25U25643G_CMD.c:97–113` uses it in the RDCR branch. `FLASH_4BYTE_MASK 0x40` at DEF.h:121 is used only by the alternate RDSCUR branch, CMD.c:115–122. CMD.h:43 identifies RDCR opcode15 and CMD.h:42 identifies RDSCUR opcode2B. Therefore FLASH-VERSION-BOUND-COMPARISON.md's claimed bit5-versus-sample-bit6 disagreement compares different registers and must be removed. No hardware bug or unresolved register-layout discrepancy follows from this evidence.

Stock 4703DC requests15, reads one byte into sp+8, and only consumes it on transport status zero at4703E4–E6. B7 command470568–56A similarly proceeds on status zero at470570–572. The read helper preserves HAL4C2098's return in r4 at4701F4 and returns it at47020C. Crucially, the mode predicate then returns1 for bit5 set,0 for clear, **or the nonzero transport error unchanged** at47042C. Its caller4705C4–C6 treats any nonzero as the proceed branch470610. Do not conflate the predicate's boolean return with HAL status zero-success, or claim this caller cleanly distinguishes readback errors from true. This is a static error-path ambiguity/opportunity, not measured hardware failure.

## Verified remaining bounded claims

Stock QE extraction at470B22–2A uses response byte shifted6 and masked1; reread comparison470CD6–CEA follows the update. Selected read stores opcode6C at471070–72. Configuration installs leading byte8 at470EAA–EAC; the acquired Apollo HAL names the device structure's leading byte ui8TurnAround. These substantiate the report's selected static contracts. Copied configuration enum identity/address-width/lane settings still need producing-version binding; byte-only Transmit and separate idle counts cannot establish physical phase widths or waveforms. No source/compiler identity follows from matching protocol behavior.

The official archive is LLD1.1b for MX25U25643GM2I00, SHA256db9f2e0f7c7d7d52121165da84ada2f800e50aa9e48e6c898404323e42c0c104. Its acquisition expressly does not verify fitted package suffix. Family agreement does not prove fitted silicon revision. No new acquisition or hardware access was needed to resolve the false disagreement.

## Evidence

[Discovery report](../source-discovery-parallel-2026-10-09/FLASH-VERSION-BOUND-COMPARISON.md), [receipt](../source-discovery-parallel-2026-10-09/FLASH-VERSION-BOUND-RECEIPT.json), [listing](../source-discovery-parallel-2026-10-09/flash-2.2.6.10-disassembly.txt), [sample CMD](../macronix-official-sample-discovery-2026-10-09/sample/MX25U25643G_CMD.c), [sample masks](../macronix-official-sample-discovery-2026-10-09/sample/MX25U25643G_DEF.h), [acquisition](../macronix-official-sample-discovery-2026-10-09/acquisition.json).

[Independent verification](FLASH-INDEPENDENT-VERIFICATION.json): all17 checks pass, comprising7 receipt file hashes,6 selected locked-image interval hashes and4 raw instruction checks. Static read-only review; no sealed test repeated, no firmware executed, no canonical/index/source changes.

## Remaining inventory lead

The prior inventory scan also found a specific public Zephyr BQ27427 CC Gain polarity workaround (drivers/sensor/ti/bq274xx/bq274xx.c) worth a bounded comparison against the stock's seven DM descriptors and emulator DM model. Existing TI TRM/hardware identification is already known. This is a possible protocol/model comparator, not stock source attribution, and has not yet been acquired or bound. Broader library references contain stale missing-snapshot claims for already registered mpaland printf, CAPSENSE, STM32 HAL and NationalChip KWS; those are ledger-maintenance issues, not new acquisition opportunities. No global exhaustion claim is justified.
