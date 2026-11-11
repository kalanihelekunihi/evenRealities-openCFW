/* SPDX-License-Identifier: MIT
 * Stock 0x3335c8 emsys_transport_idle_code_3335c8 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Returns 2 when controller_transport_idle() is 0, otherwise 1.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_controller_transport_idle(void);

uint32_t opencfw_em9305_emsys_transport_idle_code_3335c8(void)
{
  return (opencfw_em9305_controller_transport_idle() == 0u) + 1u;
}
