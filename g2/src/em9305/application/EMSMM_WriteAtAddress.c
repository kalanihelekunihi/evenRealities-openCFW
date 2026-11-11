/* SPDX-License-Identifier: MIT
 * Stock 0x305020 EMSMM_WriteAtAddress (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Magic check as above; plen >= 5: LE32 address stored at [obj+0x70], then 0x305a20(params + 4, plen - 4) writes the data. Success replies only for op 0xfd03 (otherwise returns 0 with no reply); failure clears [obj+0x70] and replies the error status.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_emsmm_write_memory_305a20(const uint8_t *src, uint32_t count);
uint32_t opencfw_em9305_EMSMM_WriteAtAddress(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t obj = W32(0x801098u);
  uint32_t magic = W32(obj + 0x68u);
  uint32_t st;
  if (magic != 0x53535353u && magic != 0xa9a9a9a9u) {
    st = 0x2fu; W32(obj + 0x70u) = 0u;
  } else if (plen < 5u) {
    st = 0x12u; W32(obj + 0x70u) = 0u;
  } else {
    W32(obj + 0x70u) = (uint32_t)params[0] | ((uint32_t)params[1] << 8) | ((uint32_t)params[2] << 16) | ((uint32_t)params[3] << 24);
    st = opencfw_em9305_emsmm_write_memory_305a20(params + 4, (uint16_t)(plen - 4u));
    if (st == 0u) {
      if (op != 0xfd03u) return 0u;
    } else {
      W32(W32(0x801098u) + 0x70u) = 0u;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
