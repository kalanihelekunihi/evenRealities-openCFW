/* SPDX-License-Identifier: MIT
 * Stock 0x305284 EMSRC_EmCoreReceiverTestEnd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc6. [0x8019a1] == 0 -> status 0xc; else weak hook 0x305930(&half = 0x7fff, 0) is the status and the reply is 5 bytes: LE16 of [0x8019a4] and the half.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_emsrc_weak_hook_305930(uint16_t *a, uint8_t *b);
uint32_t opencfw_em9305_EMSRC_EmCoreReceiverTestEnd(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  (void)plen; (void)params;
  uint16_t h = 0x7fffu;
  uint32_t st, len;
  if (B8(0x8019a1u) == 0u) {
    len = 1u; st = 0xcu;
  } else {
    uint32_t v;
    st = opencfw_em9305_emsrc_weak_hook_305930(&h, 0);
    v = W32(0x8019a4u);
    resp[4] = (uint8_t)v; resp[5] = (uint8_t)(v >> 8);
    resp[6] = (uint8_t)h; resp[7] = (uint8_t)(h >> 8);
    len = 5u;
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
