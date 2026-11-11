/* SPDX-License-Identifier: MIT
 * Stock 0x3053b4 EMSRC_EmCoreTransmitterTestEnd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc2. plen != 0 -> status 0x12, reply 1 byte. Else, if [0x8019a1] is 0: 0x3124bc() != 0 -> 0x30f1cc(2, 0), status 0; else status 0xc. If [0x8019a1] is set: status = weak hook 0x305940() (default 0xc), then up to 100 times delay 0x32 while the flag stays set, and the count is replaced by W32[0x8019a8]. Reply is status plus the LE32 count, with reply length 3 as the original passes (looks odd; kept verbatim).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_emsrc_weak_hook_305940(void);
extern uint32_t opencfw_em9305_stock_3124bc(void);
extern void opencfw_em9305_stock_30f1cc(uint32_t a, uint32_t b);
extern uint32_t opencfw_em9305_controller_rom_delay(uint32_t ms);
uint32_t opencfw_em9305_EMSRC_EmCoreTransmitterTestEnd(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t len, st, n = 0u;
  (void)params;
  if (plen != 0u) {
    len = 1u; st = 0x12u;
  } else {
    if (B8(0x8019a1u) == 0u) {
      if (opencfw_em9305_stock_3124bc() != 0u) {
        opencfw_em9305_stock_30f1cc(2u, 0u);
        st = 0u;
      } else {
        st = 0xcu;
      }
    } else {
      st = opencfw_em9305_emsrc_weak_hook_305940();
      for (;;) {
        if (B8(0x8019a1u) != 0u) {
          if ((uint8_t)n > 0x63u) break;
        } else {
          if (B8(0x8019acu) != 0u || (uint8_t)n >= 0x64u) break;
        }
        (void)opencfw_em9305_controller_rom_delay(0x32u);
        n++;
      }
      n = W32(0x8019a8u);
    }
    resp[4] = (uint8_t)n; resp[5] = (uint8_t)(n >> 8);
    resp[6] = (uint8_t)(n >> 16); resp[7] = (uint8_t)(n >> 24);
    len = 3u;
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
