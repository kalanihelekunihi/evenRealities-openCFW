/* SPDX-License-Identifier: MIT
 * Stock 0x304fa4 EMSMM_ReadAtAddress (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Magic check as above; plen == 5: params = LE32 address (kept at [obj+0x6c]) and a count byte; needs ctx >= count + 4, then 0x3059d8(resp + 4, count) reads the memory and the reply is count + 1 bytes (status 0). Any failure clears [obj+0x6c].
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern uint32_t opencfw_em9305_emsmm_read_memory_3059d8(uint8_t *dst, uint32_t count);
uint32_t opencfw_em9305_EMSMM_ReadAtAddress(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t obj = W32(((uintptr_t)&em9305_ram_801090 + 0x8u));
  uint32_t magic = W32(obj + 0x68u);
  uint32_t st, len = 1u;
  if (magic != 0x53535353u && magic != 0xa9a9a9a9u) {
    st = 0x2fu; W32(obj + 0x6cu) = 0u;
  } else if (plen != 5u) {
    st = 0x12u; W32(obj + 0x6cu) = 0u;
  } else {
    uint32_t count;
    W32(obj + 0x6cu) = (uint32_t)params[0] | ((uint32_t)params[1] << 8) | ((uint32_t)params[2] << 16) | ((uint32_t)params[3] << 24);
    count = params[4];
    if (ctx < count + 4u) {
      st = 0x12u; W32(obj + 0x6cu) = 0u;
    } else {
      st = opencfw_em9305_emsmm_read_memory_3059d8(resp + 4, count);
      if (st == 0u) len = (uint8_t)(count + 1u);
      else W32(W32(((uintptr_t)&em9305_ram_801090 + 0x8u)) + 0x6cu) = 0u;
    }
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, len, ctx, resp, 0u);
}
