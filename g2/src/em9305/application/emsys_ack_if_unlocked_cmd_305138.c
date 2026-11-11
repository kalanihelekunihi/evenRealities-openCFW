/* SPDX-License-Identifier: MIT
 * Stock 0x305138 emsys_ack_if_unlocked_cmd_305138 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Registered for HCI vendor opcode 0xfd83 (em_system table, guard 0x53535353). Replies status 1 when the NVM magic is 0x53535353 or 0xa9a9a9a9, else 0x2f; the command name is not recoverable (four identical handlers, opcodes 0xfd81..0xfd84).
 * Handler signature (r0..r4): op, plen (param byte count), params, ctx, resp; it writes the status at resp[3] and hands (op, resp length, ctx, resp, after-callback) to the resident ROM reply routine 0x102588. Status 0x12 = bad parameters, 0x2f = not allowed in this boot state.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after);
uint32_t opencfw_em9305_emsys_ack_if_unlocked_cmd_305138(uint32_t op, uint32_t plen, const uint8_t *params, uint32_t ctx, uint8_t *resp)
{
  (void)plen; (void)params;
  uint32_t magic = W32(W32(0x801098u) + 0x68u);
  uint8_t st = 0x2fu;
  if (magic == 0x53535353u || magic == 0xa9a9a9a9u) st = 1u;
  resp[3] = st;
  return opencfw_em9305_rom_em_cmd_reply_102588(op, 1u, ctx, resp, 0u);
}
