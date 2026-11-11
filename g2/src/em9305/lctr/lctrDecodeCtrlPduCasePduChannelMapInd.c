/* SPDX-License-Identifier: MIT
 * Stock 0x319268 lctrDecodeCtrlPduCasePduChannelMapInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and
 * verified against it in the QEMU-ARC harness (.waves/w28, 300 tests). Validates a channel-map PDU body: packet type 8, channel-map bits < 0x20
 * in the second word and at least 2 used channels. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dba4(uint32_t body);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low, uint32_t high);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduChannelMapInd(uint32_t pdu, uint32_t unused, uint32_t len)
{
  uint32_t body, high;
  (void)unused;
  if (len == 0u) return 0x19u;
  body = pdu + 0xcu;
  (void)opencfw_em9305_packet_child_32dba4(body);
  if (B8(pdu + 5u) != 8u) return 0x19u;
  high = W32(body + 4u);
  if (high >= 0x20u) return 0x1eu;
  return opencfw_em9305_ll_mask_count_30c414(W32(body), high) >= 2u ? 0u : 0x1eu;
}
