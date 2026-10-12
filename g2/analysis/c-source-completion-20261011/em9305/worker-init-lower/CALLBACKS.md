# Prepared EM9305 callback continuation

Two new source files are separate from the ten reviewed initializer units and
the frozen `init_lower_native.h` header:

| Native body | Prepared source | Host fixture | Unresolved children |
| --- | --- | --- | --- |
| `0x31f9b0..0x31fa0c` | `init_callback_31f9b0.c` | `verify_callback_31f9b0.c`: 144 branch/mutation cases | `0x3191dc`, `0x319714`, `0x32a000`, `0x31e4a0` |
| `0x31e7fc..0x31e848` | `init_callback_31e7fc.c` | `verify_callback_31e7fc.c`: 32 cases | `0x31e4a0`; `0x314154` binds selected `opencfw_em9305_wsf_queue_empty` |

Both source files compile under the pinned ARC GNU 2026.03 target with
`-mcpu=arcem -mcode-density -O2 -Wall -Wextra -Werror`. Native source is
`g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`, decoded from
`em-activation-round/em-inspection.bin` at base `0x302400`, SHA-256
`0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.

The `0x31e7fc` native `add3` at `0x31e82a` uses a scaled displacement:
`0x2d * 8 = 360`, now asserted in the fixture. `0x31f9b0` rereads the
record's mode byte around each child call; the fixture mutates that byte
inside child stubs. Previous 36/32 case receipts are superseded by these
corrected fixtures. Host fixtures establish bounded control, argument,
return, and read-order behavior; hardware and full child equivalence remain
unqualified.

Integration must change the frozen header's generic callback prototypes to
`uint32_t opencfw_em9305_callback_31f9b0(uint32_t context, uint32_t event)`
and `uint32_t opencfw_em9305_callback_31e7fc(void)`. No source body has been
invented for the four exposed children. The native `0x31e4a0` dispatcher
requires its full multi-state CFG and `0x323028` stack-argument ABI before
admission; `0x3191dc` uses a 43-entry product handler table at `0x334d0c`
whose targets include interior blocks, so it cannot be replaced by raw code
pointers or independent empty handlers.
