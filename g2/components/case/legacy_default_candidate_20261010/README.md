# CASE legacy no-action branch candidate

`default.c` reconstructs the no-action return of the fixed CASE legacy command entry. It reads the same log-state byte and leaves command state unchanged. It is an isolated branch child, **not** the public `case_legacy_command` provider and is not selected by `source_candidate_20261010/build.py`.

The authenticated Cortex-M0 comparison in `g2/analysis/case-legacy-default-candidate-20261010/` passes 117 original/source cases for 13 opcodes, three lengths and three initial log bytes. It checks return value, selected state bytes, lack of lower calls and non-stack writes. Opcode `0xaf` is excluded: the full original entry reaches logging for some inputs even though the table's clamped target can be a return. Other accepted command branches, side effects and hardware are outside this child.

`gpio_a1.c` adds the isolated `0xa1` branch. It enforces the stock length guard and forwards byte 1 bit `0x10` then bit 0 to separate lower GPIO calls. Its verifier passes 96 stock/source cases across four lengths, six payload bytes, two log flags and two controlled lower-return words. It compares ordered child call arguments, return value and state writes. It does not select the full legacy handler or claim physical GPIO effects.

`log_toggle_af.c` covers the distinct `0xaf` path that precedes the Thumb table. For length at least two it writes the boolean log-state byte; a nonzero payload calls the logger twice with source-owned `"%02x"` and `"\r\n"` strings. Its controlled logger oracle passes 80 stock/source cases across length, byte, initial flag and logger-return variants. This does not claim the formatter or physical output.

`reset_toggle_ae.c` covers opcode `0xae`: length guard, boolean write to `0x200000c0`, and conditional source-owned `"%s reset GLS"`/newline logger calls. The authenticated original/source oracle passes 120 cases and compares both state bytes, logger format and string argument, returns, and non-stack writes. The logger remains a lower cut.

`version_a0.c` covers opcode `0xa0` with source-owned version and format strings. Its original/source oracle passes 144 cases, comparing logger format, pointed-to version, counter argument, ordered calls, return and state. The fixture also mutates the log flag after the second call to verify the stock reload path. Logger implementation and physical output remain lower boundaries.

`scan_a2.c` covers opcode `0xa2`: eight-byte fill, hex-log handoff and conditional eight-byte formatted report with a source-owned format string. Its controlled lower-call oracle passes 108 original/source cases, including mutation of the buffer and log flag after the hex handoff. The lower fill, hex logger and formatter remain explicit boundaries.

`status_a3.c` covers opcode `0xa3` with three controlled value producers and two source-owned status format strings. The authenticated full-entry comparison passes 96 cases, checking child order/output words, eight variadic logger words, flag reload after a controlled logger mutation, return and state. The producers and logger remain lower boundaries.

`word_a4.c` covers `0xa4` with a source-owned `%d` format and log-state reload. Its oracle passes 144 cases, including a logger-induced flag change between the two possible reports.

`set_sn_a5.c` covers the `0xa5` length guard, optional source-owned `Set SN:` label, eight-byte hex handoff and Set SN child call. Its oracle passes 72 cases. The lower serial-number write is controlled, not physically validated.

`control_aa_ab.c` covers the last two distinct `0xa0..0xaf` table action targets: `0xaa` chains two explicit lower calls and `0xab` calls one lower child. Its authenticated full-entry oracle passes 36 cases across opcode, length, initial flag and child-return vectors. Those child implementations and effects remain outside the branch proof.

`control_b0.c` covers high opcode `0xb0`, forwarding the word at `0x200000f0` and span 256 to the stock-address lower child; its oracle passes 54 cases. `known_dispatch.c` compiles a bounded routing interface for the independently compared branches. It returns `false` for unsupported opcodes and is not the public legacy handler; its routing composition has not yet received a whole-entry oracle.

`charging_d2.c` covers the high opcode `0xd2` length guard, boolean write to `0x20000105`, and conditional source-owned charging log. Its full stock-entry oracle passes 120 cases. The bounded dispatcher recognizes `0xd2` but still returns false for unsupported high opcodes and is not selected as the public handler.

`pmic_d4.c` covers high opcode `0xd4`: optional source-owned PMIC message/newline, then lower child with R0=20 and R1=8. Its authenticated full-entry oracle passes 48 cases. The bounded dispatcher recognizes `0xd4`; PMIC effects and the public handler remain open.

`simulate_d1.c` covers high opcode `0xd1` with a length-four guard, boolean writes to `0x200000c1..c3` and conditional source-owned format text. Its full stock-entry oracle passes 120 cases, including all three variadic words. The bounded dispatcher recognizes `0xd1`; formatter/output remain lower boundaries.

`toggle_dd.c` covers high opcode `0xdd`, which reads byte 1 regardless of logical length, booleanizes it and writes `0x200000bd`. Its authenticated full-entry comparison passes 120 cases. The input buffer is allocated beyond the logical length in the fixture; this does not prove safe parsing of a short physical frame. The bounded dispatcher recognizes `0xdd` while the public handler remains unresolved.

`dogfeed_df.c` covers high opcode `0xdf`: length-two guard, boolean write at `0x200000be`, and conditional source-owned dog-feed text. Its full stock-entry oracle passes 120 cases. The bounded dispatcher recognizes `0xdf`; formatter/output remain lower boundaries. The `0xdd` short logical-length caveat remains unchanged.

`charging_status_d3.c` covers high opcode `0xd3` as a read-only state report with source-owned charging text. Its authenticated full-entry oracle passes 120 cases; it returns directly when logging is disabled. The bounded dispatcher recognizes `0xd3`, and the lower formatter/output remain explicit.

`watchdog_d0.c` covers high opcode `0xd0`: length guard, boolean watchdog-set child call, fresh log-state read, then optional source-owned watchdog text. The full-entry oracle passes 240 cases, including a child-induced log-state change. Watchdog hardware effects remain an explicit lower cut; the bounded dispatcher recognizes `0xd0`.

`shipmode_ee_prefix.c` covers the `0xee` USB-present return path and compares the USB-absent path only to first standby child `0x080035d4`; 72 authenticated cases pass. `reset_ff_prefix.c` compares `0xff` only to first reset child `0x0800502c`; 36 cases pass. Neither is routed by `known_dispatch.c` because the lower nonreturning paths and effects are still open. The `0xdd` short physical-frame caveat persists.

The 256-opcode stock census now runs five logical lengths and two log states (2,560 cases); the only lower-boundary hits outside the bounded dispatcher are `0xee` and `0xff`. A separate authenticated source comparison passes 3,450 no-action cases for all 230 other previously unsupported opcodes at five lengths and three log states. `known_dispatch.c` now routes those proven fallbacks to `case_legacy_default_branch`, so it handles 254 opcode values under its bounded input allocation; `0xee`/`0xff` remain explicit `false` because their lower paths are only prefix-proven. This remains a non-public dispatcher, not an archive provider. Valid decoded `de` outer frames can pass logical length zero; all oracle buffers allocate 32 bytes and do not prove physical short-frame safety, including the `0xdd` byte-1 read.

A linked Cortex-M0+ fixture now combines all 254 supported branch sources with `known_dispatch.c`. Its authenticated full stock-entry/source oracle passes 2,540 cases (254 opcode values, five logical lengths, two log states), comparing dispatcher result, state, non-stack writes, and normalized lower call arguments under controlled child stubs. This is a linked test ELF, **not** the selected CASE archive. `0xee` and `0xff` remain unsupported due to standby/reset lower paths. The `0xdd` physically short-frame caveat remains.

`reset_child_502c.c` is an isolated source model of stock `0x0800502c`. The 36-case `verify_ff_reset_sequence.py` full-entry oracle matches logger calls, AIRCR write and idle-loop revisit through this child. Emulator execution does not prove physical reset. Public legacy selection is still gated by `0xee` standby lowers, physical effects, and the `0xdd` short-frame issue; the 254/256 dispatcher remains test-only.

`binary_unknown_candidate.c` is an isolated binary destination-2 fallback, verified against the authenticated stock full entry in 168 cases. It handles seven sampled non-special opcode values under an allocated 256-byte input contract; destination-not-2 has different stock behavior. It is not `case_binary_command` and is not selected into the CASE archive.

`binary_51_candidate.c` covers one destination-2 binary special opcode. Its 45-case authenticated full-entry comparison controls the fill child and stops at send with an exact 12-byte reply check. It is isolated and not selected as the full binary provider.

`binary_5f_candidate.c` covers destination-2 opcode `0x5f`, verified in 45 authenticated full-entry cases through a controlled 16-byte fill child and exact 20-byte send payload. It remains isolated from the public binary provider.

`binary_14_candidate.c` covers destination-2 opcode `0x14` with four controlled value-child calls and source-owned 11-byte reply. Its authenticated full-entry oracle passes 96 cases through send entry; it is not selected as full binary handler.

`binary_06_41_candidate.c` covers destination-2 acknowledgment and one-byte legacy handoff prefixes for opcodes `0x06` and `0x41`. The 48-case authenticated full-entry oracle stops before legacy entry; reset, standby and send effects remain open.

`binary_3e_candidate.c` covers destination-2 opcode `0x3e` through the ack lower, including state comparison, boolean write, word clear, conditional control and logging. Its authenticated full-entry oracle passes 288 cases; physical aging and send effects remain unclaimed.

`binary_3f_candidate.c` covers destination-2 opcode `0x3f` through its acknowledgment boundary. The authenticated 96-case full-entry oracle includes logger mutation of output state; the enable child and physical output remain lower gates.

`binary_5e_candidate.c` covers the destination-2 `0x5e` short-length, apply-success and apply-failure branches through the hex lower. Its authenticated full-entry oracle passes 120 cases; apply/send/hex effects remain controlled boundaries.

`binary_56_candidate.c` and `binary_3d_candidate.c` cover two more isolated binary routes with authenticated full-entry comparisons (216 and 192 cases). `0x3d` is the destination-not-2 prelude through its dispatch child; other non-2 opcodes share a separate forwarding path. All 14 visible binary special values have bounded or prefix evidence, but the public binary handler remains unselected.

`binary_forward_candidate.c` and expanded fallback oracles cover all 255 non-`3d` opcodes on the non-destination-2 path and all 243 non-special opcodes on the destination-2 fallback, respectively. `binary_known_dispatch.c` links ten bounded candidate bodies for test use and explicitly rejects six destination-2 values. Its 65,536-pair native routing test does not establish a full public binary handler; lower effects and selected archive remain open.

`binary_local_four_candidate.c` extends destination-2 `50`/`5c`/`5d`/`68` comparison to logging-enabled inputs (1,620 authenticated cases). The test dispatcher now rejects only `06`/`41`; its linked Cortex-M0+ wrapper passes 5,370 no-lower and 480 controlled-local full-entry comparisons. All linked composition remains test-only, and the selected CASE archive is unchanged.

Nested binary handoff oracles now pass 48 cases for `0x41` through the emulator-visible reset loop and 144 cases for `0x06` to the first standby child. Neither establishes physical reset/standby or a public binary provider. `binary-lower-census.json` classifies 33 test lower aliases: 22 map to selected CASE source (with explicit return ABI/effect caveats), 11 exact child names remain unowned.

`binary_value_readers_candidate.c` sources stock 0x08009ff0 and 0x0800a01e with explicit byte/word read lowers; 36 direct and 216 linked full-entry comparisons pass. `binary_flash_fill_candidate.c` sources stock 0x08002f60/0x08002f88 as blockwise-reversed copies from external runtime flash addresses 0x0803f800/0x0803f000; 24 direct and 72 linked comparisons pass using synthetic flash patterns. Four original child names are closed in the test graph, seven remain, and two nested read lowers are newly exposed. No source was added to the selected archive.

Round 35: `binary_3f_enable_candidate.c` sources stock child `0x0800d154` as four ordered setter calls. Direct oracle 8 cases and linked branch oracle 96 cases pass. Setter `0x080099e8` remains a controlled lower. Test composition: 17 providers, 31 lower names (22 selected-source aliases, six original children, three nested lowers). No selected CASE archive change.

Round 36: `binary_3f_set_candidate.c` sources stock `0x080099e8` shadow cache and return ABI. Direct oracle 96 cases and linked opcode-3f branch oracle 96 cases pass with program lower controlled. Test composition: 18 providers, 31 lower names (22 selected-source aliases, six original children, three nested lowers). The remaining setter lower is `case_binary_3f_program` at stock `0x08009108`; no physical bus claim or selected CASE archive change.

Round 37: `binary_3f_program_candidate.c` sources stock `0x08009108` retry, counter and timeout logging wrapper with controlled bus/formatter lowers. Direct oracle 64 cases and linked opcode-3f branch oracle 192 cases pass. Test composition: 19 providers, 32 lower names (23 selected-source aliases, six original children, three nested read/bus lowers). No physical bus or selected CASE archive claim.

Round 38: `binary_sensor_read_lower_candidate.c` sources stock byte adapter `0x0800a124` (36 direct cases); `binary_guarded_sensor_candidate.c` sources stock guard `0x080035b8` (216 direct cases). Linked opcode-14 oracle passes 216 cases through both to controlled transaction `0x080028b4`. Test composition: 21 providers, 32 lower names (23 selected-source aliases, six original children, three nested lowers). Physical sensor/transport and selected archive remain open.

Round 39: Seven sensor-transaction children and six output-bus helpers inventoried. Isolated sensor start pulse `0x0800a4b4` passes 12 direct cases but stays outside linked graph. Word reader `0x0800a074` passes 48 direct cases and counted adapter `0x0800a130` passes 144; linked opcode-14 passes 216 through both. Test composition: 23 providers, 32 lower names (23 selected-source aliases, six original children, three nested transaction/delay/bus lowers). Physical line/timing/product state blocks production admission; selected CASE archive unchanged.

Round 40: six historical child names audited. Source-owned signed scale (`0x0800018c`), shared dispatch copy (`0x080001b4`, two exact-address aliases), `0x56` exit (`0x080012e4`) and `0x14` B reader (`0x08009f18`) pass direct and linked stock/source oracles. Only original `case_binary_5e_apply` remains unowned; physical flash effects block admission. Test graph 28 providers, 31 lower names (26 selected-source aliases, one original child, four nested lowers). Selected CASE archive unchanged.

Round 41: isolated `binary_5e_retry_failure_candidate.c` matches stock `0x0800373c` on 18 controlled three-read-failure cases, including configuration state, wait/error logging, finalization call and R0. It is intentionally outside the linked test graph and selected archive. The success path writes at external flash `0x0803f000`/`0x0803f008`; source data and flash initialization/read/write/finalization effects remain unproved. This completes the present local CASE source audit, not the public binary provider. Test graph stays 28 providers/31 lower names; selected archive stays 43 objects/70 providers/three imports (10/12 direct). See analysis REPORT Round 41 for exact remaining contracts.
