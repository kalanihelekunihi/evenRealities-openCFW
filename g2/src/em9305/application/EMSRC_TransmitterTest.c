/* SPDX-License-Identifier: MIT
 * Stock 0x3055ac EMSRC_TransmitterTest (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcodes 0xfcc1 and 0xfcca (second command table) and 0xfccb. 0xfccb -> status 0x11; 0xfcc1/0xfcca -> status = 0x333a94(plen, params, resp, &len) with the reply length from the out byte len (starts at 1); any other opcode -> 1.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_stock_333a94(uint32_t plen, const uint8_t *params, uint8_t *resp, uint8_t *len);
uint32_t opencfw_em9305_EMSRC_TransmitterTest(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint8_t len = 1u;
  uint32_t st;
  if (op == 0xfccbu)
    st = 0x11u;
  else if (op == 0xfccau || op == 0xfcc1u)
    st = opencfw_em9305_stock_333a94(plen, params, resp, &len);
  else
    st = 1u;
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
