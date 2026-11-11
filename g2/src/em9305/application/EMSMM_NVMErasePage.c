/* SPDX-License-Identifier: MIT
 * Stock 0x304f44 EMSMM_NVMErasePage (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Magic must be 0x53535353 or 0xa9a9a9a9 (else 0x2f); plen == 2 with params {0, page < 0x40} or {1, page < 4} (bank select, page) runs 0x30ef14(bank != 0, page): status 0 if it returns 0 else 3; otherwise 0x12.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_stock_30ef14(uint32_t flag, uint32_t page);
uint32_t opencfw_em9305_EMSMM_NVMErasePage(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t magic = W32(W32(0x801098u) + 0x68u);
  uint8_t st = 0x2fu;
  if (magic == 0x53535353u || magic == 0xa9a9a9a9u) {
    st = 0x12u;
    if (plen == 2u) {
      uint32_t sel = params[0], page = params[1];
      if ((sel == 0u && page < 0x40u) || (sel == 1u && page < 4u))
        st = (opencfw_em9305_stock_30ef14(sel != 0u, page) == 0u) ? 0u : 3u;
    }
  }
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
