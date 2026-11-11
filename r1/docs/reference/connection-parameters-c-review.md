# R1 connection-parameter policy in C

`native_connection_parameters.c` supplies the product-specific BLE observer
at stock `0x51aa0`, the fast-interval classifier at `0x72b80`, and packed
delayed dispatch at `0x882ac`. The observer is invoked through the existing
reconstructed priority-one table. It queries connection role before dispatch,
preserves the observed connect/update/disconnect branches and dual log gates,
and calls the existing delayed schedule/cancel APIs.

The classifier reads the maximum interval halfword at parameter offset 2 and
returns whether it is below 50. The observer preserves the native state updates,
the special 36/39 interval-pair condition and the scheduling argument reload
after logging. Delay values remain the observed raw 2000/4 values; no inferred
timing conversion or retry policy is added.

The packed callback uses the upper 16 bits as handle and the low eight bits as
opcode, ignoring the middle byte. Handle `0xffff` produces no provider call.
Opcodes 0/1/2 forward commands 64/16/32, zero length and null payload to the
existing BLE message encoder; other opcodes go to the existing error provider.
Both handoffs retain the caller's SP/LR and callee registers. This supplies the
actual callback rather than leaving a new unresolved dispatch boundary.

Only four observed flag bytes are owned: three bytes at `0x200064be` and one
at `0x200064f6`. Executing the stock RW decoder gives initial bytes `00000100`,
matching the C sections. The known neighboring connection-handle slices do not
overlap these fields. No complete enclosing context layout is invented, and
test placement does not prove the final source RAM map.

REA/Ghidra read the observer, classifier, callback and log literals. The observer
frontier span is corrected from 472 to 474 code bytes to include its final
branch at `0x51c78`; the following alignment bytes and literals are excluded.
All recorded byte windows were checked against the locked application.

The actual production object passed:

- 2,528 paired observer cases through the actual reconstructed table, including
  role and event branches, threshold/special intervals, glasses/phone/neither
  handle matches, log modes, repeated provider changes and interrupt masks.
  Scheduled callbacks execute after observer return in the fixture.
- All 65,536 maximum-interval values through both native and C classifier leaves.
- 7,680 paired packed-callback cases covering handle boundaries, all opcodes,
  middle-byte variations and both PRIMASK settings, with strict zero-frame tail
  handoff checks for SP, LR and all callee registers.
- Six observer/classifier negative controls and five callback controls, including
  wrong threshold/delay/argument, wrong phone flag, omitted cancellation, invalid
  packed decoding and a retained callback frame.

The observer remains a bounded candidate: native provider depth is 40 bytes;
C depths are 48 or 72. Role, logging, handle queries, scheduling/cancellation,
encoding and error providers are modeled. The synthetic callback-consumption
step does not validate actual scheduling or message delivery. Void returns and
other caller-clobbered values, APSR, live observer callee registers and private
spills are excluded. Radio operation, real timing, arbitrary aliases, faults
and concurrency remain unproven. The callback's zero-frame handoffs are checked
separately; its full code is not byte-identical.

The normal build compiles/composes 591 R1 units without known failures or
duplicate strong symbols. All 590 prior objects are byte-identical. The manifest
only adds this unit. Application imports decrease from 158 to 157; bootloader
imports remain 34, with no new imports introduced. The new source contains no
inline assembly.

Exact qualification selected no new regions. The source plan and hybrid
application retain locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,269 source-built, 641,891 binary-pull-through and 248 resource bytes.
Complete source linking, hardware support and a byte-identical source rebuild
remain unfinished.

The [receipt](connection-parameters-c-review.json) records compiler arguments,
hashes and evidence. Ignored reproduction inputs are under
`build/goal-r1-connection-parameters-c/`; current reports are
`build/sources-goal-r1-connection-parameters-c-final/report.json` and
`build/hybrid-goal-r1-connection-parameters-c-final/build-report.json`.
