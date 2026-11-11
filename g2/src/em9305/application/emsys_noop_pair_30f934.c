/* SPDX-License-Identifier: MIT
 * Stock 0x30f934 emsys_noop_pair_30f934 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Calls the two empty functions 0x30fab0 and 0x30f6d8 in turn.
 */
#include <stdint.h>
extern void opencfw_em9305_emsys_noop_30fab0(void);
extern void opencfw_em9305_emsys_noop_30f6d8(void);

void opencfw_em9305_emsys_noop_pair_30f934(void)
{
  opencfw_em9305_emsys_noop_30fab0();
  opencfw_em9305_emsys_noop_30f6d8();
}
