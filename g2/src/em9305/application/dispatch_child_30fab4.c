/* SPDX-License-Identifier: MIT
 * Stock 0x30fab4 dispatch_child_30fab4 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Tail call to common_activate_310580 (R0 preserved); the sibling at 0x30fab8 is dispatch_child_30fab8.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_common_activate_310580(uint32_t);

uint32_t opencfw_em9305_dispatch_child_30fab4(uint32_t value)
{
  return opencfw_em9305_common_activate_310580(value);
}
