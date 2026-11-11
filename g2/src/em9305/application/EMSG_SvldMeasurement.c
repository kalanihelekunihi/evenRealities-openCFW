/* SPDX-License-Identifier: MIT
 * Stock 0x304e74 EMSG_SvldMeasurement (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). plen == 0: timer_enable(1), reply of 3 bytes (status 0, byte [0x80199c], byte [0x8019a0] + 1); else status 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
extern uint32_t opencfw_em9305_timer_enable(uint32_t enable);
uint32_t opencfw_em9305_EMSG_SvldMeasurement(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t len = 1u;
  uint8_t st = 0x12u;
  (void)params;
  if (plen == 0u) {
    (void)opencfw_em9305_timer_enable(1u);
    resp[4] = (uint8_t)W32(0x80199cu);
    resp[5] = (uint8_t)(B8(0x8019a0u) + 1u);
    len = 3u; st = 0u;
  }
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
