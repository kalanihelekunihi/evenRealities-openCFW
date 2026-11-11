/* SPDX-License-Identifier: MIT
 * Stock 0x305358 EMSRC_EmCoreTransmitterTest (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc1. Parameter check 0x333b48(params, plen, 0) fails -> status 0x12. Else with p5 = (int8_t)params[5]: params[0] != 0 -> EMSystem_TransmitCM(p5, params[0], params[1], params[4], resp, &len); params[0] == 0 -> weak hook 0x30593c(p5, params[3], params[2], params[4], params[1], resp, &len) (default returns 0xc). The out byte len (starts at 1) is the reply length.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_stock_333b48(const uint8_t *params, uint32_t plen, uint32_t zero);
extern uint32_t opencfw_em9305_stock_305ab4(int32_t a, uint32_t b, uint32_t c, uint32_t d, uint8_t *resp, uint8_t *len);
extern uint32_t opencfw_em9305_emsrc_weak_hook_30593c(int32_t a, uint32_t b, uint32_t c, uint32_t d, uint32_t e, uint8_t *resp, uint8_t *len);
uint32_t opencfw_em9305_EMSRC_EmCoreTransmitterTest(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint8_t len = 1u;
  uint32_t st = 0x12u;
  if (opencfw_em9305_stock_333b48(params, plen, 0u) != 0u) {
    int32_t a = (int8_t)params[5];
    if (params[0] != 0u)
      st = opencfw_em9305_stock_305ab4(a, params[0], params[1], params[4], resp, &len);
    else
      st = opencfw_em9305_emsrc_weak_hook_30593c(a, params[3], params[2], params[4], params[1], resp, &len);
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
