/* SPDX-License-Identifier: MIT
 * Stock 0x304e4c EMSG_SetUartBaudRate_Callback (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Delay 1000 ms, interrupts off (clri/sync), ROM 0x104b98([(uintptr_t)&em9305_ram_80f978]) (the ROM routine name is inferred from this being its only caller), interrupts on (seti).
 * ROM calls go through opencfw_em9305_rom_* facades (em9305_link_closure.c).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
extern void opencfw_em9305_rom_uart_set_baud_104b98(uint32_t value);
void opencfw_em9305_EMSG_SetUartBaudRate_Callback(void)
{
  opencfw_em9305_rom_delay_1020e8(1000u);
  (void)__builtin_arc_clri(); __builtin_arc_sync();
  opencfw_em9305_rom_uart_set_baud_104b98(W32((uintptr_t)&em9305_ram_80f978));
  __builtin_arc_seti(0);
}
