/* SPDX-License-Identifier: MIT
 * Stock 0x304c0c emsys_reset_cmd_304c0c (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). plen == 0 -> status 0 and callback 0x304c30 (clear PML mode flags, reset); otherwise 0x12. Name not recovered (the em_system command id is not known from the sources).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
extern void opencfw_em9305_emsys_reset_cb_304c30(void);
uint32_t opencfw_em9305_emsys_reset_cmd_304c0c(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  (void)params;
  resp[3] = (plen == 0u) ? 0u : 0x12u;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, (plen == 0u) ? (uint32_t)(uintptr_t)opencfw_em9305_emsys_reset_cb_304c30 : 0u);
}
