# OpenCFW shortcut-theory continuation frontier, 2026-10-09

This continuation used three GPT-6.1 Sol low-reasoning tracks after the prior
public-source inventory reached its first finite boundary. It applies the newly
registered tools and performs deeper official history/source comparisons without
crossing the active P2 gate. No canonical ledger, firmware source, installed
processor, authenticated input, or workflow gate was changed.

## Net new knowledge

### Authenticated C-SKY recovery and processor repair

- Reconciled canonical child/codec/runtime coordinates and recovered four
  startup bodies (244 instruction bytes), ten direct callees (982 bytes), 24 XIP
  lifecycle/mode/app bodies (1,446 bytes), and eight final provider-boundary
  bodies (210 bytes): **2,882 scoped instruction bytes** total. These are private
  reviewed candidates, not accepted campaign coverage.
- Found and privately repaired a second C-SKY Ghidra defect: MFCR constructors
  wrote control-register values to a temporary rather than the declared
  destination register. The corrected SLEIGH compiled and passed authenticated
  reset/system-init probes; global and pinned processor sources remain unchanged.
- Recovered stage1 NOR routing, fixed UART 115200 behavior, stage2 BSS clearing,
  ordered MPU/VIC setup, wake-source logic, main IDLE/TWS lifecycle dispatch,
  queue behavior, watchdog setup, and initialized application callbacks.
- Public NationalChip archives provide exact or relocation-qualified matches for
  wake/start-mode, analog update, clock/LDO, interrupt-enable, audio-exit and
  SNPU-exit providers. SNPU init differs only in literal-pool encodings and is
  deliberately not labelled exact. Public lifecycle C constrains KWS/audio/PMU
  structure; the remaining application request/event helpers are first-party
  firmware semantics rather than a missing third-party-source search.

### ARM/Ablation/REA shortcuts

- Promoted Apollo main `0x004CFF6C..0x004CFF9A` from link-order speculation to
  instruction-backed TLSF `mapping_insert`, then closed adjacent
  `mapping_search`. Main configuration is 32 second-level bins, four-byte
  alignment, minimum block 12, maximum block `0x40000000`, and 24 first-level
  lists. Two 3,560-case suites plus 13 locate-prefix and 13 adjustment cases
  passed against original instructions. Overflow behavior and caller limits are
  recorded rather than sanitized.
- Ablation accelerated direct-call discovery but its string and argument
  heuristics were not reliable evidence. REA added provenance/orchestration but
  no independent ISA or mapping proof.
- Closed the stock `0xFFF2` tail question: authenticated scatter initialization
  zeros `0x20074150..0x20074158`; original command and copy instructions produce
  `FF 7C 01 0F B8 19 00 00`. The command itself rewrites only bytes 0..5, so
  later unknown mutation remains a separate lifetime/alias obligation.

### Deeper vendor history and configuration evidence

- Added official Infineon MSCLP demo pin
  `2944e6269b1f17771176275dec8e8649fc853309` as
  `third-party/reference/infineon-msclp-demo`. Its generated Configurator XML
  supplies schema/vocabulary but not the target's missing generated C.
- Mapped recovered LP/slider fields to official CapSense concepts. A useful
  negative discriminator rejects direct reuse: the demo enables LP raw IIR while
  stock `CE_CTL=0x80000100` leaves that enable bit clear, despite matching some
  coefficient/default values.
- Excluded STM32CubeG0 v1.6.3's official G0B1 FreeRTOS Timers MDK project as the
  case producing recipe: it selects ArmCC 5.06 and the RVDS CM0 port, conflicting
  with the stock Arm Compiler 6 plus GCC-port fingerprint.
- Ambiq SDK 5.2 alpha2-to-alpha3 changes the inspected EM9305 helper only by a
  revision comment. NationalChip public pins remain unchanged, and no public
  historical EM9305 v4.2 implementation appeared.

## Current dependency-source boundary

The new public third-party/dependency inference frontier is exhausted for the
bounded branches inspected here. Repeating release/tag searches, TLSF mapping
fixtures, generic CapSense parameter fitting, or lifecycle skeleton matching
would not add defensible source identity.

Remaining work now belongs to different evidence classes:

- independent review and canonical admission of the private P2 records;
- first-party G2 application-state/protocol semantics and full indirect-target
  ownership;
- private HAL/Nema/EM9305 sources, original compiler projects, generated target
  CapSense configuration, resident-ROM contracts, or hardware/runtime traces;
- whole-artifact byte-ledger and pseudocode completion under the existing
  campaign procedure.

These are not solved by another generic dependency download. Newly available
authentic inputs can reopen the source frontier. No cybersecurity classifier
blocked any phase, so Daybreak Blue was not needed. G2 remains `P2_EXECUTING`;
G2 through G6 remain unopened.

## Evidence

- `../shortcut-csky-authenticated-20261009-agent1/REPORT.md`
- `../shortcut-csky-authenticated-20261009-agent1/callees/REPORT.md`
- `../shortcut-csky-authenticated-20261009-agent1/xip-lifecycle/REPORT.md`
- `../shortcut-csky-authenticated-20261009-agent1/final-source-boundary/REPORT.md`
- `../shortcut-arm-tools-20261009-agent3/REPORT.md`
- `../shortcut-arm-tools-20261009-agent3/search-successor/REPORT.md`
- `../shortcut-arm-tools-20261009-agent3/fff2-tail/REPORT.md`
- `../shortcut-vendor-history-20261009-agent2/REPORT.md`
- `../shortcut-vendor-history-20261009-agent2/touch-schema-successor/REPORT.md`
