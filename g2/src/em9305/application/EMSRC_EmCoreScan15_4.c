/* SPDX-License-Identifier: MIT
 * Stock 0x3052dc EMSRC_EmCoreScan15_4 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcce. If the parameter check 0x333674(params, plen) passes, the weak hook 0x305938(params[0], params[1], LE16(params + 2), resp, &len) is the status and its out byte sets the reply length (starts at 1); else status 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_stock_333674(const uint8_t *params, uint32_t plen);
extern uint32_t opencfw_em9305_emsrc_weak_hook_305938(uint32_t a, uint32_t b, uint32_t c, uint8_t *resp, uint8_t *len);
uint32_t opencfw_em9305_EMSRC_EmCoreScan15_4(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint8_t len = 1u;
  uint32_t st = 0x12u;
  if (opencfw_em9305_stock_333674(params, plen) != 0u)
    st = opencfw_em9305_emsrc_weak_hook_305938(params[0], params[1], (uint32_t)params[2] | ((uint32_t)params[3] << 8), resp, &len);
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
