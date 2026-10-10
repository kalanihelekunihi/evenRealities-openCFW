# Cordio signaling-length guard: nine offline comparisons

**Stock matches the guard-bearing SDK source projection in all nine fixtures; old r20.05c differs on lengths0–3.** This establishes the selected parser's local pre-lookup length guard and dispatch ABI. It does not establish whole Cordio revision, caller safety, upstream delivery, downstream parsing, or live Bluetooth behavior.

New source hypothesis came from discovery's authenticated SDK5.2 `l2c_main.c`: new `L2C_CHECK_DATA_LENGTH(len,4)` before connection lookup, absent in public r20.05c. This is distinct from all previously closed IOM/DSP/LZ4/Nema/audio work. Public comparator pinned `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; full file acquired with Apache-2.0 notice, hash`b76edc13a463028e60c6b148d90c47bc9dbb8f2a8783ac8efc1f765fc722d951`. SDK full file hash`16de435673010a4de3c1b182012981f53684703c4a0a982df9e117f8a0d8284f` matches discovery's ZIP provenance. The harness extracts each complete function body verbatim and supplies documented types/constants/macros and dependency mocks; it does not compile the entire Cordio module or claim source byte equality.

## Original-byte proof

Locked main payload hash`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. Complete selected stock `[0x53076E,0x5308E6)`376bytes/hash`c26ae1510d3d56ca5de518313cd89389c877a3f1047c4512ab0a547e05db9f7d` is retained as original hex and full disassembly. Payload offset=VA-0x438000+32.

Entry preserves handle r0→r5, length r1→r4, pointer r2→r6. At0x530778 UXTH zero-extends length; compare4 at0x53077A and BLT.W0x5308E4 at0x53077C precede connection BL0x530784→0x4B6E96. Role BL0x530796→0x4B73C4 occurs only after nonzero byte connection ID. Control-block literal0x530B90 holds0x200737D8. Master role0 loads callback+24, slave role1 loads+28; BLX at0x5307BA/0x5307DC passes unchanged pointer with zero-extended handle/length. Nonconfigured role follows trace branches, then all paths join original POP at0x5308E4. Complete extent includes its logging control flow; branch absence is not inferred from a tiny compare alone.

## Nine fixtures and explicit supplied dependencies

| Direct parser fixture | Stock and SDK observable result |
|---|---|
| Length0 | No lookup/role/dispatch/trace |
| Length1 | No lookup/role/dispatch/trace |
| Length2 | No lookup/role/dispatch/trace |
| Length3 | No lookup/role/dispatch/trace |
| Length4, no connection | One handle lookup only |
| Length4, master+callback | Handle lookup, role lookup, one master callback |
| Length4, slave+callback | Handle lookup, role lookup, one slave callback |
| Length4, master+null callback | Handle lookup, role lookup, one recorded trace event; no dispatch |
| Length65535, master+callback | Unsigned-length ordinary dispatch; direct ABI case only |

All callback arguments are handle0x123, exact length, guest packet pointer0x20090000. Each guest buffer has32 initialized readable bytes even for logical length0–3; callbacks are recording mocks and never parse packet contents. Arm control-block callback slots are32-bit Thumb pointers; host-source fields are separately mapped by name and are not treated as stock struct-layout evidence. Packet/control bytes, R4–R7 and SP remain unchanged in all cases.

Original parser instructions run in Unicorn2.1.4 with Thumb/M-class mode. Connection0x4B6E96 and role0x4B73C4 return fixture values; fake master/slave callbacks record arguments and return. No real connection table, scheduler, controller, transport or downstream handler executes. Model boundary violations stop with an unmodeled-provider error.

Trace policy is explicit: stock platform trace-enable query0x4C9C50 returns0; all six query visits in the null-callback case are retained separately as platform-probe events. Original fallback logger0x52A63C is a logged return-only dependency recording role from r2. Source `L2C_TRACE_ERR1` maps to a trace event with the same role. Comparison is **semantic event projection**, not identity of raw logger-internal calls or log formatting. The raw stock query sequence is preserved in ninecase-results.json; no real logger executes. Other trace configurations and their format/filter children are untested.

Old r20.05c dispatches each short logical length through connection/role lookup and callback in these supplied states; stock/SDK do not. Five other fixture projections agree across all three. Void returns are not used as an outcome substitute: call ordering, callback arguments, state/buffer guards and ABI preservation are checked. No mutant sweep or additional fixtures were added.

## Caller and scope limits

Read discovery's CALLER-AND-FIXTURE-CONTRACT.md: length is L2CAP payload length while pointer remains original HCI packet start. Authenticated caller uses32-bit framing equality payload+4==uint16 HCI length, so65535 cannot pass that caller; this case tests direct unsigned ABI only. Caller could statically admit payload0–3 when framing is coherent, but actual allocation/reassembly/controller delivery and downstream stock handlers are unproved. Direct-target fixtures do not execute caller or WsfMsgFree and do not transfer ownership. No vulnerability or physical-Bluetooth claim follows.

SDK guard matches a software variant; producing private revision and other release changes remain unknown. Local callbacks are mocks rather than validated downstream providers. No source-completeness/canonical coverage counter changes were made.

Touch overlap check is additive in TOUCH-COVERAGE-OVERLAP.md: earlier72-byte constructor result exactly overlaps the already completed startup-provider packet underlying the1074 candidate census. **Zero new touch coverage** is claimed; prior seals remain unchanged.

Preservation.json records prior seals,110 protected inputs and four checkpoints. Index unchanged during ninecase run and stable during preservation verification; cross-track sample difference is separately reported. Only this unique analysis directory and a narrow public-source fetch were written. No production/submodule-pin/index/commit/push/device actions. Initial sandbox native-Unicorn mapping failed before fixture execution; permitted execution recovered it, with no model substitution.

Replay: `python3 g2/analysis/cordio-signaling-length-ninecase-20261009-implementation/run.py` with the existing local Unicorn dependency path and native mapping permissions; `preserve.py` checks prior packets. Source and runtime identity, original receipts, ninecase-results and harnesses are retained. Independent fixture review remains required before any canonical admission; no missing input blocks this local conclusion.
