/* SPDX-License-Identifier: MIT
 * Stock 0x3054f0 emsrc_receiver_test_end_3054f0 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc6 (second command table). Name inferred from the opcode and the first table; the real symbol name is not recoverable. plen != 0 -> status 0x12; else command_stop_30b654(&cfg) != 0 -> status 0xc; else if ctx >= 4 the reply is status 0 plus LE16 of cfg[0] >> 16 and one byte from 0x302760(cfg[2], cfg[3], cfg[4] & 0xffff, 0); ctx < 4 -> 0x12. ctx is the third argument of the ROM reply call.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_command_stop_30b654(uintptr_t output);
extern uint32_t opencfw_em9305_stock_302760(uint32_t a, uint32_t b, uint32_t c, uint32_t d);
uint32_t opencfw_em9305_emsrc_receiver_test_end_3054f0(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t cfg[5];
  uint32_t st = 0x12u, len = 1u;
  (void)params;
  if (plen == 0u) {
    uint32_t r = opencfw_em9305_command_stop_30b654((uintptr_t)cfg);
    uint32_t v = opencfw_em9305_stock_302760(cfg[2], cfg[3], cfg[4] & 0xffffu, 0u);
    if (r != 0u) {
      st = 0xcu;
    } else if (ctx >= 4u) {
      uint32_t c = (cfg[0] >> 16) & 0xffffu;
      st = 0u; len = 4u;
      resp[4] = (uint8_t)c; resp[5] = (uint8_t)(c >> 8); resp[6] = (uint8_t)v;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
