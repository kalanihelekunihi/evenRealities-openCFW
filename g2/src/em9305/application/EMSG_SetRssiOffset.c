/* SPDX-License-Identifier: MIT
 * Stock 0x304db0 EMSG_SetRssiOffset (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). plen == 1: 0x3122f0((int8_t)params[0]) (stores the byte at 0x80fd5e), status 0; else 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
extern void opencfw_em9305_emsrc_set_rssi_offset_3122f0(int32_t offset);
uint32_t opencfw_em9305_EMSG_SetRssiOffset(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint8_t st = 0x12u;
  if (plen == 1u) {
    opencfw_em9305_emsrc_set_rssi_offset_3122f0((int8_t)params[0]);
    st = 0u;
  }
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
