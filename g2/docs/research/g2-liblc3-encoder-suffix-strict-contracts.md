# G2 liblc3 encoder suffix strict-contract authentication

Status: all seven minimum-suffix relocation contracts are authenticated and
applied. LC3 placement and routing remain blocked on separate integration work.

## Scope and evidence boundary

The capacity audit identified seven source-owned closures which any contiguous
30,516-byte Apollo-main shrink must move. The machine-readable authority is
`components/apollo_main/liblc3_encoder/suffix_strict_contracts.json`. It pins:

- the repaired Apple component (`898d5efb...`, 3,885,668 bytes), core report,
  overlay configuration, and capacity proposal;
- the scan and formatter sources plus their directly included header/template;
- exact current and proposed relocation tables and symbol types; and
- the Ghidra function-range export used to reject four false branch decodes.

The analyzer compiles with Apple Clang 21 for `thumbv7em-none-eabi`, invokes
the core builder's strict extractor, and replays every relocation at both the
current and conditional stable-repack address. It does not perform the repack,
place LC3, route `service_audio`, or exercise hardware.

## Exact contracts

| Closure | Current | Proposed | Bytes | Relocations | Result |
|---|---:|---:|---:|---:|---|
| `open_cfw_runtime_strtod_bounded` | `0x007E4FC0` | `0x007DE5A0` | 2,696 | 27 | strict-authenticated |
| `open_cfw_runtime_strtod` | `0x007E5A48` | `0x007DF028` | 10 | 1 | strict-authenticated |
| `open_cfw_runtime_scanset_match` | `0x007E5A54` | `0x007DF034` | 126 | 0 | strict-authenticated |
| `open_cfw_runtime_vsscanf` | `0x007E5AD4` | `0x007DF0B4` | 2,530 | 2 | strict-authenticated |
| `open_cfw_runtime_sscanf` | `0x007E64B8` | `0x007DFA98` | 28 | 1 | strict-authenticated |
| `open_cfw_runtime_iar_scanf_core` | `0x007E64D4` | `0x007DFAB4` | 12 | 1 | strict-authenticated |
| `open_cfw_runtime_iar_vsnprintf_engine` | `0x007E64E0` | `0x007DFAC0` | 3,508 | 12 | strict-authenticated |

All proposed entries move by exactly -27,168 bytes. The 44 reviewed ELF
relocations comprise 40 `R_ARM_THM_CALL`, two `R_ARM_THM_JUMP24`, one
`R_ARM_THM_MOVW_PREL_NC`, and one `R_ARM_THM_MOVT_PREL` record. Each selected
closure is global, default-visible `STT_FUNC`; scan siblings are defined
`STT_FUNC`; runtime imports are undefined `STT_NOTYPE`.

Strict extraction reproduces the canonical current bytes for all seven
closures. Replaying the same exact contracts at the proposed addresses also
succeeds, including all branch-range checks.

## Formatter-engine repair

The former specialization embedded the stale recursive pointer `0x007F7061`
through a MOVW/MOVT/BLX sequence with no ELF relocation. The maintained wrapper
now dispatches `%PV`/`%pV` recursion directly to
`open_cfw_runtime_iar_vsnprintf_engine`. Apple Clang emits one
`R_ARM_THM_CALL` at engine offset `0x4BC`; its symbol is the selected whole
global/default Thumb `STT_FUNC`, and its target is resolved to the engine's
actual placement.

The extractor keeps this capability fail closed. Same-section recursion is
rejected unless `allow_self_relocation` is explicitly enabled together with a
strict `R_ARM_THM_CALL`, exact `STT_FUNC`, exact runtime target, and a whole
same-section global/default Thumb symbol. Focused hostile tests reject an
unused opt-in, `JUMP24`, wrong type/target, and local or partial symbols.

The new engine is 3,508 bytes, four bytes shorter than the prior engine. The
builder admits exactly four reviewed zero-fill bytes before
`open_cfw_runtime_iar_format_bridge`, keeping that bridge and every later leaf
at its previous address. The Apple canonical receipts are:

- core overlay: 362,272 bytes, `8c80c3fa...`;
- core-stage component: 3,885,668 bytes, `696e5cf5...`;
- final component: 3,885,668 bytes, `898d5efb...`; and
- LTPF intermediate component: 3,885,668 bytes, `7cfe8499...`.

The Linux profile remains byte-identical because these formatter leaves are
Apple-gated: final overlay `4caa6c35...` (154,604 bytes) and component
`45d32718...` (3,678,000 bytes).

## Ingress and remaining blockers

The repaired component still contains exactly six external entry branches to
the suffix: three calls and three jumps, plus no raw 32-bit entry pointer. Four
halfword-offset false decodes remain classified as the second halfwords of
authenticated UDIV/SDIV instructions.

The minimum suffix contract blocker set is now empty, but production capacity
rebalancing remains fail closed. The current builder does not yet place source
closures into authenticated stock slots or perform stable repack relocation
replay. Owner-relative fixed targets and two PT source-UART receipts must be
refreshed after such a move. Final LC3 import binding, writable-data policy,
service-audio lifetime adaptation, and routing are also absent.

No live-hardware conclusion follows from this software audit. Audio cadence,
quality, BLE transport, stack use, timing, and microphone behavior remain
outside its evidence boundary.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_suffix_contracts.py --pretty
python3 -m unittest -v \
  g2.tests.test_analyze_g2_liblc3_encoder_suffix_contracts
```

The tests run the analyzer twice and compare output bytes, assert exact ingress
and relocation totals, and prove that demoting the repaired engine contract
fails closed.
