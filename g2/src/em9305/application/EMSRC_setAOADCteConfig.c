/* SPDX-License-Identifier: MIT
 * Stock 0x305658 EMSRC_setAOADCteConfig (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcce (second command table). plen == 7 -> 0x311f70(int16 LE(params+0), int16 LE(params+2)) and 0x311f84(int16 LE(params+4)), status 0; other lengths -> 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern void opencfw_em9305_stock_311f70(int32_t a, int32_t b);
extern void opencfw_em9305_emsrc_store_aoa_value_311f84(int32_t a);
uint32_t opencfw_em9305_EMSRC_setAOADCteConfig(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t st = 1u;
  if (op == 0xfcceu) {
    st = 0x12u;
    if (plen == 7u) {
      opencfw_em9305_stock_311f70((int16_t)(uint16_t)(((uint32_t)params[1] << 8) | params[0]),
                                  (int16_t)(uint16_t)(((uint32_t)params[3] << 8) | params[2]));
      opencfw_em9305_emsrc_store_aoa_value_311f84((int16_t)(uint16_t)(((uint32_t)params[5] << 8) | params[4]));
      st = 0u;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
