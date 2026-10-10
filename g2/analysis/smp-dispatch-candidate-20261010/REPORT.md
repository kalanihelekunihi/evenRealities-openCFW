# SmpHandler C candidate: finite component result

## Completed scope and denominator

One of one assigned bounded handler bodies is now source-defined and compiled:
stock main `0x537d0c..0x537e9e`, 402 bytes, 161 decoded instructions, 24 direct
BL sites to 11 unique providers. This denominator covers SmpHandler only. It
does not measure whole Bluetooth or full firmware completion. There is no
locally justified whole-Bluetooth function denominator for this assignment.

Round1 implemented dispatch, CMAC cleanup, CCB checking, current/stale AES
selection, the entire five-stage logging cascade, and queue drain. Round2
validated 45 scripted original-byte versus compiled-native-C fixtures: all45
agree, every one of the161 instruction starts and all24 call sites execute at
least once. The fixtures include null messages, event32, event28 with zero and
nonzero plaintext words, other events, open/closed connections, token equality,
empty/multiple message drains, logging levels1..4 with bit1 clear/set and high
flag bits, final logging gate/match, and nonzero comparison return carry into
later logging gates. Input message/CCB bytes remain unchanged; original stack
and r4..r7 preservation are checked on every case. Queue providers are scripted
callbacks here; the prior `smp-stale-queue-20261010` five-fixture artifact
separately exercised authentic queue/free wrappers and queue-dequeue body.

Build succeeded with Apple clang21.0.0, warnings treated as errors, C11. It
emits both Cortex-M55 Thumb freestanding object and native dylib. Native compiled
C behavior is crosschecked against original Thumb instructions in Unicorn;
the M55 object is compile evidence, not an executed hardware binary.

## Evidence and ABI

Main hash is checked before each validation run:
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Handler body hash:
`c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba`.
Retained GNU force-Thumb/Ablation/REA instruction receipts bound all161 starts
and all24 direct sites. Native source projection source/API evidence supplies
the void return, event/message prototype and explicit DM caller; message r1,
event/status offsets2/3, param truncation to low byte, plaintext word offset8,
CCB offsets61/65 and ignored input event are independently stock-instruction
observations. No fabricated CCB-null guard or return status is introduced.

Live Ghidra-MCP `list_open_programs` was unavailable to this model. REA's live
Ghidra12.1.4 function dossier succeeded using the authenticated analysis-only
ELF; `rea-high-pcode.json` retains decompilation and355 high-Pcode operations.
The flow reports no truncation and zero known omitted operations/inputs/edges.
The synthetic ELF contains only this body: literals and provider bodies/callers
are absent. Therefore Ghidra types and out-of-body literal values are not used
as independent authority. Literal values come from hash-pinned main bytes;
caller/type observations also use the retained authenticated SDK source. No
live GUI program was modified. High Pcode remains decompiler evidence.

## Remaining work and effort

Handler semantics: zero assigned handler control paths left unimplemented;
45/45 fixtures agree. Provider semantics: all11 provider implementations remain
external boundaries in this candidate (table in component README). Existing
authenticated provider/source evidence can inform separate assignments, but
this candidate does not count those implementations as complete. Production
integration needs data relocation, scheduler registration/ABI wrapper, concrete
CCB/queue/lifetime contracts, providers and target linker placement. Each is a
separate dependency task; reliable duration estimates require assigning those
bodies and their own evidence denominators.

Byte equality: not achieved. Source candidate uses provider/context arguments
and compiler-selected codegen. `results.json` records the ARM object identity
and its `.text` comparison. Exact codegen requires the authenticated producer
compiler/version/options and final linked contracts; the present clang object
is not a byte-identical replacement. No opcode arrays, donor executable content,
traps, or invented provider returns are linked into this source candidate.
Authenticated original bytes are used solely by the validator.

This is isolated user-authorized candidate work. Shared builds, campaign state,
coverage corpus and G3/G4 gate records were not modified or claimed passed.
