# NFCT IRQ, field handling and TIMER4 C integration

Stock NFCT IRQ `0x3060c` and field/check/frame-delay helpers now route to the
existing, unchanged pinned Nordic SDK `nrfx_nfct.c`. REA covers the 480-byte IRQ
body and helper bytes. Application vector 21 contains `0x3060d`. No firmware
implementation, state owner, source unit, compiler flag or manifest is changed.

The fixture links the actual NFCT object with the actual timer C object, executing
TIMER4 clear/enable helpers during field detection. Their frontier receipts are
also updated for this TIMER4 instance/silent-diagnostics domain, without extending
the result to other instances or logging modes. The native log-mode getter
also executes; its RAM mode byte `0x200068ec` is explicitly zero. Logging-enabled
behavior is outside this evidence. Critical-section and other unused driver APIs
are removed by normal section garbage collection, not replaced by stubs.

Compiled assertions confirm the 16-byte NFCT control block, 16-byte event and
12-byte timer-workaround structure. Native addresses are bound for controlled
execution: NFCT state `0x2002c2bc`, timer state `0x2002c2a4` and workaround
`0x2000796c`. The compiler over-aligns the NFCT object section to eight bytes;
the test linker uses SUBALIGN(4), matching the C type's natural four-byte alignment
and native address. This is a test placement, not proof of a final firmware link.
The actual native startup decoder independently produces the same 12 initialized
workaround bytes as the C initializer. Cold BSS initialization is not established
by that initializer check.

81,272 paired two-IRQ sequences pass (162,544 invocations):

- 65,536 cover all eight-event pending/enabled-mask combinations while the field
  filter is active.
- 256 cover field on/off/ambiguous transitions, filter state, field status and
  null/non-null callbacks, including actual TIMER4 activation.
- 15,360 exercise RX/TX bit-count boundaries, CRC subtraction, frame/error status
  masks, cached frame delay and null/non-null callbacks.
- 120 change packet metadata, masks, handler pointers, field/filter state or
  cached delay during callbacks.

Ordered NFCT/TIMER4 MMIO, meaningful callback fields, callback-visible driver,
workaround and timer state, final mapped register/state memory, return callee
registers, SP, interrupt masks and adjacent state guards match. Eight negative
controls reject ignored enables, included RX CRC bits, retained TX interrupts,
ignored field filtering, missing timer enable, wrong SELECTED delay, retained RX
status and retained field-on state.

Field detection arms the TIMER4 workaround and records the field transition;
field loss returns NFCT to SENSE and disables the RX/TX interrupt group. Field
filtering suppresses transitions until released. RX end reports whole bytes after
CRC subtraction and masked frame errors. TX end disables its interrupt group.
SELECTED clears stale frame events and status and restores cached delay. Timeout
errors and TX-start metadata follow the stock callback ordering. Short RX lengths
also preserve stock's wrapped subtraction; these controlled inputs are not a claim
that all combinations are physically valid on-air frames.

Native callback depths are 56/88 bytes versus C's 32/72, with private event offsets
also differing. Event padding, private addresses, live callback registers and
caller-clobbered return state are excluded. INTENSET/CLR and status write-one-to-
clear behavior are modeled with bounded MMIO observers. Real RF fields, protocol
interactions, autonomous EasyDMA, timer/clock timing, physical IRQ/exception delivery,
arbitrary aliases/faults and concurrency remain unproven.

Qualification compiles the NFCT unit and selects no exact regions. All 590 normal
source/object hashes and the manifest were revalidated against the prior passing
R1 report, with 164 application / 34 bootloader imports, no compile failures and
no duplicate strong symbols. The retained canonical hybrid and current source-plan
hash are unchanged: 4,245 source-built, 641,915 executable fallback and 248 resource
bytes. Source-built includes admitted assembly/data. Complete source-only rebuilding
and byte-identical C reconstruction remain unproven.

Machine-readable evidence: `nfct-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-nfct-irq-c/`.
