/* SPDX-License-Identifier: MIT
 * Stock 0x305844 EMSS_LeEncryptKC (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfc89. Same as EMSS_LeDecryptKC but the ROM 0x10093c call has the decrypt flag 0 (encrypt).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_rom_le_cipher_kc_10093c(uint32_t selector, const uint8_t *key, uint8_t *buffer, uint32_t decrypt);
uint32_t opencfw_em9305_EMSS_LeEncryptKC(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint8_t key[16], buf[16];
  uint32_t st, len = 1u, i;
  if (plen != 0x11u) {
    st = 0x12u;
  } else {
    uint32_t r;
    for (i = 0u; i < 16u; i++) key[i] = params[16u - i];
    for (i = 0u; i < 16u; i++) buf[i] = 0u;
    r = opencfw_em9305_rom_le_cipher_kc_10093c(params[0], key, buf, 0u);
    if (r == 1u) {
      st = 3u;
    } else if (r != 0u) {
      st = 0x1fu;
    } else {
      for (i = 0u; i < 16u; i++) resp[4u + i] = buf[15u - i];
      st = 0u; len = 0x11u;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
