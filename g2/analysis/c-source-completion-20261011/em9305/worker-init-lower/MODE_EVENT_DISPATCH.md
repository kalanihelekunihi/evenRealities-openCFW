# Prepared connected 0x31e4a0 mode/event dispatcher

`init_child_31e4a0_connected.c` reduces the complete native envelope
`0x31e4a0..0x31e5ea` into one provider. Inputs are `R0=context` and
`R1=event`; the body does not consume incoming `R2`. State byte
`context+1` is captured once. The state 0 question-mark sequence,
state 2 special event and L/M fallthrough, state 3 Q transition, common
L/M release path, and default event dispatcher are represented. The
`BC` after `CMP(event-71,2)` is the unsigned LO case, so events 71/72
take the default path. No interior branches are represented as functions.

The call to native `0x323028` has eight register arguments and six caller
stack words. The C declaration has fourteen arguments in that order.
Target ARC disassembly of the prepared call stores six words at caller
`sp+0..20` and places `R0..R7` before `BL`, matching the native caller's
`0x31e55e..0x31e578` sequence. The stack words are configuration words
at `+76,+80`, zero, context bytes `+321,+890`, and context halfword `+892`.
The source preserves the native volatile read sequence that builds them.

Native listing: `g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`
from `em-activation-round/em-inspection.bin`, base `0x302400`, SHA-256
`0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.
The prepared C unit compiles with ARC GNU 2026.03,
`-mcpu=arcem -mcode-density -O2 -Werror`. Its twelve unresolved symbols
include two existing selected providers (`associated_schedule_drop_3136ac`
and `init_connection_release_31ad90`) and ten genuine child bodies.

`verify_child_31e4a0_connected.c` passes twelve bounded host fixtures,
including state/flag mutation across callbacks, all major branch groups,
the fourteen-argument child call, and the L/M return path. It does not
execute native ARC instructions or prove the ten child bodies, final RAM
contents, placement, or hardware behavior. This candidate is prepared and
unselected; the two packet dispatcher candidates remain frozen.
