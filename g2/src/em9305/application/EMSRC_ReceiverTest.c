/* SPDX-License-Identifier: MIT
 * Stock 0x305448 EMSRC_ReceiverTest (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). HCI opcodes 0xfcc5, 0xfccc and 0xfccd (second command table). 0xfccd -> status 0x11; 0xfcc5/0xfccc: receiverTestCheckParameters(params, plen, op == 0xfccc) failing -> 0x12, else a 20-byte config (params[0], params[1], params[6] for 0xfccc, flags 1 and 2, params[2..5] copied) goes to command_30cba0 whose result is the status; any other opcode -> status 1.
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
extern void *opencfw_em9305_memset(void *dst, uint32_t value, uint32_t count);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_stock_3335f4(const uint8_t *params, uint32_t plen, uint32_t mode);
extern uint32_t opencfw_em9305_command_30cba0(uintptr_t input);
uint32_t opencfw_em9305_EMSRC_ReceiverTest(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  uint32_t cfg[5];
  uint8_t *b = (uint8_t *)cfg;
  uint32_t st;
  if (op == 0xfccdu) {
    st = 0x11u;
  } else if (op == 0xfcccu || op == 0xfcc5u) {
    st = 0x12u;
    if (opencfw_em9305_stock_3335f4(params, plen, op == 0xfcccu) != 0u) {
      (void)opencfw_em9305_memset(cfg, 0u, 0x14u);
      b[8] = params[0];
      b[9] = params[1];
      if (op == 0xfcccu) b[10] = params[6];
      b[0xd] = 1u;
      b[0xe] = 2u;
      (void)opencfw_em9305_memcpy(b + 4, params + 2, 4u);
      st = opencfw_em9305_command_30cba0((uintptr_t)cfg);
    }
  } else {
    st = 1u;
  }
  resp[3] = (uint8_t)st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
