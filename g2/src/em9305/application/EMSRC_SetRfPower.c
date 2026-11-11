/* SPDX-License-Identifier: MIT
 * Stock 0x30555c EMSRC_SetRfPower (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc4 (second command table). plen == 1 and (int8)params[0] < 0x15 -> prev = radio_status_311a00(1), mode = radio_mode_312290(level), command_vendor_byte_30cee4(level); the reply is status 0 plus prev and mode; otherwise status 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_radio_status_311a00(uint32_t query);
extern uint32_t opencfw_em9305_radio_mode_312290(uint32_t mode);
extern uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t value);
uint32_t opencfw_em9305_EMSRC_SetRfPower(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t st = 0x12u, len = 1u;
  if (plen == 1u && (int32_t)(int8_t)params[0] < 0x15) {
    uint32_t prev = opencfw_em9305_radio_status_311a00(1u);
    uint32_t mode = opencfw_em9305_radio_mode_312290((uint32_t)(int32_t)(int8_t)params[0]);
    (void)opencfw_em9305_command_vendor_byte_30cee4((int32_t)(int8_t)params[0]);
    st = 0u; len = 3u;
    resp[5] = (uint8_t)mode;
    resp[4] = (uint8_t)prev;
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
