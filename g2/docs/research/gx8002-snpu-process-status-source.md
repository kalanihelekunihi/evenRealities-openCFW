# GX8002 SNPU status-processing candidate

Stock package0xf164/runtime0x10205bd8 spans264 bytes. Pinned SDK snpu.o names
snpu_process_status; GRUS callback types come from authenticated gx_snpu.h.
The source candidate and builder are runtime_gx8002_snpu_process_status.c and
build_gx8002_snpu_process_status_candidate.py. The function is now qualified and registered. Compilation alone was not
used as evidence of completion.

Observed behavior:
- Read interrupt events through the live register pointer, then clear the
  non-overflow events through a fresh pointer read.
- Event1 takes priority over all error paths. Read completed command address.
  If it equals state+5d0, return0. Otherwise update5d0, snapshot read index5b0
  and end index5b4, and iterate task records (144-byte stride, ten-entry ring).
- For each old index, callback/module/private fields are at record+90/94/98hex.
  Advance the local index with the original signed remainder-by10 behavior.
  If it reaches the captured end index, set next_state=STALL2 and suspend.
  That next_state remains2 on subsequent iterations. Initial state isBUSY1.
- If state_base+old_index*144+16 equals completed+0x20000000, write state and
  the advanced index, optionally invoke the callback, and return0. Otherwise
  optionally invoke the callback and keep iterating, without a timeout.
- With no completion event, bit8 or bit4 triggers overtime reset and return0.
  Bit32 reads overflow address, reloads the register pointer, performs the
  otherwise-unused observable read of5b0, clears overflow, and returns0.
- Otherwise return1 when bit64 is set, else2. C-SKY MVCV negates the condition
  bit into bit0, clearing all other bits (ISA manual text10636 onward), which
  establishes this final result rather than assuming a generic success code.

The callback header establishes module_id, GX_SNPU_STATE, and private_data
argument order. Numeric offset views do not claim full driver-state recovery.
Control-word meanings in TCB initialization remain a separate unresolved area.

Build experiments: initial integer-address view produced292 bytes and a
60-byte frame. A typed callback field view reduced code to260. With
-fno-move-loop-invariants, final candidate232 bytes/frame44; originalframe56.
Only the final qualified candidate is admitted. The recorded compiler option avoids excess saved
loop constants; no assembly or extracted bytes are used as payload.

Qualification requirements included all event priority combinations, duplicate/new
completion, each ring start/end/target position, multiple callbacks, null
callbacks, changing state/pointers at helper/callback boundaries, snapshot end
index, sticky STALL state, output scratch behavior, preserved callback args
across suspend, signed index arithmetic within documented valid domains,
never-matching completion prefixes, exact read/write ordering, ignored helper
returns, all return paths and ABI. Examine the candidate disassembly for
instruction forms when maintaining its interpreter. Completed qualification
and its scope limits are recorded below.

Qualification checkpoint: 14,048 completed cases and120 bounded nonmatching
ring prefixes pass decoded stock/source comparison against an independent
state/call model. All10 start/end/target positions are covered, with null,
mixed and full callback sets, pointer/callback mutations, low-seven-bit event
combinations plus ignored high bits and duplicate completions. Model source
hash is included in reviewed evidence. Eighteen tests include mutation checks
for event gates, private-data restore, final index, return selection and frames.
Ring indices are restricted to valid0..9; invalid memory/index behavior is not
claimed. Local scratch addresses are normalized while bounds and initialization
remain checked. Helpers and physical hardware timing are separate obligations.

Integrated candidate passes all512 tests. The former264-byte retained region
is now232 compiled C bytes plus32 bytes of generated unreachable fill.
Reviewed report: gx8002-snpu-process-status-verification.json.
