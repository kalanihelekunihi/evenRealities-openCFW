# smpSmExecute bounded source candidate

The fixed main flash body at `0x56ee62..0x56f144` (738 bytes) is represented by `execute.c` plus the previously verified `dispatch_tail.c`. The source owns the entry guard, enabled and disabled logging cascades, trace fallback, role based transition table selection, state update, and indirect action dispatch. It calls eight lower providers through an explicit `g2_smp_execute_providers` table; no provider implementation is inferred from the call site.

## Provenance

- Official OTA: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, stripped first 32 bytes, mapped at `0x438000`, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.
- Body disassembly: `g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt` at `0x56ee62..0x56f144`; literal pool `0x56f144..0x56f178` checked directly against OTA bytes.
- Tail source: `g2/components/main/smp_sm_dispatch_tail_20261010/dispatch_tail.c`; its separate 162 comparison receipt remains valid.
- Full source: `g2/components/main/smp_sm_execute_candidates_20261010/execute.c`.

## Verification

`verify.py` compiles both C translation units for Cortex-M55 with `-Wall -Wextra -Werror`, also compiles Cortex-M4 copies to execute in Unicorn, and compares stock entry execution against source entry execution. The 768 passing fixtures cover four entry modes (global disabled, null config pointer, config byte disabled, enabled), every one of five log gate positions and all gates false, both comparator outcomes, both flag bit-1 outcomes, two events, two states, and zero/nonzero connection IDs. It compares ordered provider call names and arguments, final CCB/message bytes, and stack return. There are 23 distinct provider call shapes. `results.json` records hashes and counts.

The stock path is entered at `0x56ee62`, rather than at the previously isolated tail. For each run both paths use synthetic RAM for CCB, config, transition rows, fallback, handlers, and provider table. Lower calls return scripted gate, comparator, flag, and name values; logging and action callbacks record arguments. Thus the comparison establishes this function's local control flow and boundary arguments. It does not establish logger formatting, allocated CCB lifetime, transition table initialization, or protocol action bodies. The direct SMP body count can advance from 9/11 to 10/11 after parent integration; extended log `0x43d574` remains the other unowned direct body.
