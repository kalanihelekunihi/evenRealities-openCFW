/* SPDX-License-Identifier: MIT
 * Stock 0x3058c0 EMSS_LeRand (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfc87. plen != 0 -> status 0x12. Else builds a baseband config on the stack ({u16 512, u8 1, u32 320} plus the 6-byte table 0e 0c 0c 0e 0c 0c), calls pal_rom_baseband_init(cfg, table) and rom_random_10a7f8(cfg, 2, out8); non-zero -> status 0x1f, else status 0 and the 8 random bytes in resp[4..11] (reply length 9). The rest of the config struct is left uninitialised, as in stock; byte 3 of the first word is zeroed here (guess: harmless).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_pal_rom_baseband_init(uintptr_t config, uintptr_t table);
extern uint32_t opencfw_em9305_rom_random_10a7f8(uintptr_t config, uint32_t count, void *out);
uint32_t opencfw_em9305_EMSS_LeRand(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t cfg[11];
  uint8_t tbl[6] = { 0x0eu, 0x0cu, 0x0cu, 0x0eu, 0x0cu, 0x0cu };
  uint8_t out[8];
  uint32_t st = 0x12u, len = 1u;
  (void)params;
  if (plen == 0u) {
    cfg[0] = 0x10200u;
    cfg[1] = 320u;
    (void)opencfw_em9305_pal_rom_baseband_init((uintptr_t)cfg, (uintptr_t)tbl);
    if (opencfw_em9305_rom_random_10a7f8((uintptr_t)cfg, 2u, out) != 0u) {
      st = 0x1fu;
    } else {
      (void)opencfw_em9305_memcpy(resp + 4, out, 8u);
      st = 0u; len = 9u;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
