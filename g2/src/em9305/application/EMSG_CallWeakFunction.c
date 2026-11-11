/* SPDX-License-Identifier: MIT
 * Stock 0x304bb4 EMSG_CallWeakFunction (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Accepts only when the NVM magic word at [[0x801098]+0x68] is 0xa9a9a9a9 and plen == 0, then asks the ROM to run 0x304bf8 after the reply.
 * ROM calls go through opencfw_em9305_rom_* facades (em9305_link_closure.c).
 */
#include <stdint.h>
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void opencfw_em9305_EMSG_CallWeakFunction_Callback(void);
uint32_t opencfw_em9305_EMSG_CallWeakFunction(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t magic = W32(W32(0x801098u) + 0x68u);
  uint8_t st = (plen == 0u) ? 0u : 0x12u;
  (void)params;
  if (magic != 0xa9a9a9a9u) st = 0x2f;
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, (plen == 0u && magic == 0xa9a9a9a9u) ? (uint32_t)(uintptr_t)opencfw_em9305_EMSG_CallWeakFunction_Callback : 0u);
}
