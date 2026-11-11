/* SPDX-License-Identifier: MIT
 * Stock 0x304cac EMSG_GetEmCoreInformation (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). plen == 0 -> reply of 6 bytes (status 0 then 00 00 6e 2f 61), else status 0x12 and 1 byte. The five data bytes are copied verbatim; their meaning is not recovered.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_rom_delay_1020e8(uint32_t ms);
extern void em9305_rom_system_reset_103f14(void);
uint32_t opencfw_em9305_EMSG_GetEmCoreInformation(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t len = 1u;
  uint8_t st = 0x12u;
  (void)params;
  if (plen == 0u) {
    st = 0u; len = 6u;
    resp[5] = 0u; resp[4] = 0u; resp[6] = 0x6eu; resp[7] = 0x2fu; resp[8] = 0x61u;
  }
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
