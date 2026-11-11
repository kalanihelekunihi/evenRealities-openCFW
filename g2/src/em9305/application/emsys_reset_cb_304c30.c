/* SPDX-License-Identifier: MIT
 * Stock 0x304c30 emsys_reset_cb_304c30 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Callback of 0x304c0c: PML_ClearModeFlag(); PML_ClearConfigurationModeFlag(); system reset (ROM 0x103f14).
 * ROM calls go through opencfw_em9305_rom_* facades (em9305_link_closure.c).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
extern void opencfw_em9305_PML_ClearModeFlag(void);
extern void opencfw_em9305_PML_ClearConfigurationModeFlag(void);
void opencfw_em9305_emsys_reset_cb_304c30(void)
{
  opencfw_em9305_PML_ClearModeFlag();
  opencfw_em9305_PML_ClearConfigurationModeFlag();
  em9305_rom_system_reset_103f14();
}
