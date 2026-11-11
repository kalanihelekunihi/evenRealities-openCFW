/* SPDX-License-Identifier: MIT
 * Stock 0x305328 EMSRC_EmCoreStartAdvPattern (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc9. plen != 0 -> status 0x12; else if the receiver-test-active byte [0x8019a1] is 0 the weak hook 0x305934 (default returns 0xc) is the status, else 0.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_emsrc_weak_hook_305934(void);
uint32_t opencfw_em9305_EMSRC_EmCoreStartAdvPattern(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t st = 0x12u;
  (void)params;
  if (plen == 0u) {
    st = 0u;
    if (B8(0x8019a1u) == 0u) st = opencfw_em9305_emsrc_weak_hook_305934();
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
