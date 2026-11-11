/* SPDX-License-Identifier: MIT
 * Stock 0x304d20 EMSG_SetBootModeFlags_Callback (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Rewrites bits 16/17 of 0xf00430 from the stored mode (3: both, 1: bit 16, 2: bit 17, 0: neither) then resets; modes above 3 return without a reset. Each non-zero case first stores the cleared value, then re-reads and stores the set value.
 * ROM calls go through opencfw_em9305_rom_* facades (em9305_link_closure.c).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
#define PML_MODE_REG 0xf00430u
void opencfw_em9305_EMSG_SetBootModeFlags_Callback(void)
{
  volatile uint32_t *r = (volatile uint32_t *)(uintptr_t)PML_MODE_REG;
  uint32_t v;
  switch (B8(0x801994u)) {
  case 3u:
    v = *r; v &= ~0x10000u; v &= ~0x20000u; *r = v;
    v = *r; v |= 0x10000u; v |= 0x20000u; *r = v;
    break;
  case 1u:
    v = *r; v &= ~0x10000u; v &= ~0x20000u; *r = v;
    v = *r; v |= 0x10000u; *r = v;
    break;
  case 2u:
    v = *r; v &= ~0x10000u; v &= ~0x20000u; *r = v;
    v = *r; v |= 0x20000u; *r = v;
    break;
  case 0u:
    v = *r; v &= ~0x10000u; v &= ~0x20000u; *r = v;
    break;
  default:
    return;
  }
  em9305_rom_system_reset_103f14();
}
