# Prepared connected 0x319714 dispatcher

`init_child_319714_connected.c` source-reduces native `0x319714..0x3197c6`
as one C provider. The 17-row `BIH` table at `0x319736..0x319756`
indexes packet opcodes `3..19`; every row is represented in the switch.
No interior table targets are declared as functions. Native `R0/R1/R2`
carry context, packet, and mode. `LDB.AB` advances the packet pointer past
the opcode, so the three copy calls on opcode 3 consume payload offsets
`0`, `10`, `18` with lengths `8`, `8`, `4`; opcode 4 copies 12 bytes.
The opcode store at context+8 occurs on the invalid route as its branch
delay-slot effect.

Native listing: `g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`
from `em-activation-round/em-inspection.bin`, base `0x302400`, SHA-256
`0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.
The two unresolved callees in the compiled object are existing selected
source providers: `opencfw_em9305_short_header_decode_32dedc` and
`opencfw_em9305_memcpy`. The latter's forward copy semantics and access
widths remain its selected provider contract.

`verify_child_319714_connected.c` passes 410 host route fixtures covering
all 17 opcodes, two header lengths, three modes, two state values and two
feature-flag values, plus two invalid opcodes. ARC GNU 2026.03 compiles
the candidate with `-mcpu=arcem -mcode-density -O2 -Werror` and reports
only the two selected provider imports. This source is prepared only;
independent native execution, final placement and hardware operation are
separate qualification gates.
