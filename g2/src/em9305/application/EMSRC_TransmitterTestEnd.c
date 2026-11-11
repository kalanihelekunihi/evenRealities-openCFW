/* SPDX-License-Identifier: MIT
 * Stock 0x3055f8 EMSRC_TransmitterTestEnd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcode 0xfcc2 (second command table). plen != 0 -> status 0x12; else command_stop_30b654(&cfg): non-zero -> 0x3124bc() then 0x30f1cc(2, 0), status 0 if 0x3124bc() was non-zero (count 0); zero -> LE16 count from cfg[0]. The reply length is 3 (status + LE16).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_command_stop_30b654(uintptr_t output);
extern uint32_t opencfw_em9305_stock_3124bc(void);
extern void opencfw_em9305_stock_30f1cc(uint32_t a, uint32_t b);
uint32_t opencfw_em9305_EMSRC_TransmitterTestEnd(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t cfg[5];
  uint32_t st, len;
  (void)params;
  if (plen != 0u) {
    len = 1u; st = 0x12u;
  } else {
    uint32_t v;
    (void)opencfw_em9305_memset(cfg, 0u, 0x14u);
    st = opencfw_em9305_command_stop_30b654((uintptr_t)cfg);
    if (st != 0u) {
      uint32_t ok = opencfw_em9305_stock_3124bc();
      opencfw_em9305_stock_30f1cc(2u, 0u);
      v = 0u;
      if (ok != 0u) st = 0u;
    } else {
      v = cfg[0] & 0xffffu;
    }
    resp[4] = (uint8_t)v; resp[5] = (uint8_t)(v >> 8); resp[6] = 0u; resp[7] = 0u;
    len = 3u;
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
