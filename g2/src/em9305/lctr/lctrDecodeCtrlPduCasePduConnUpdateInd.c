/* SPDX-License-Identifier: MIT
 * Stock 0x31936c lctrDecodeCtrlPduCasePduConnUpdateInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and
 * verified against it in the QEMU-ARC harness (.waves/w28). Validates an LL_CONNECTION_UPDATE_IND body (packet type 0xc): interval in
 * [6,0xc80] (7.5 ms..4 s in 1.25 ms units), window nonzero and < min(interval,9), interval >= the +0xe halfword, supervision timeout in
 * [0xa,0xc80] and (latency+1)*interval < timeout*4 (the Core-spec supervision rule, 10 ms units vs 1.25 ms units), latency < 500.
 * Field names are not recovered (offsets only). mpywhul is the ARCv2 DSP 32x16 unsigned multiply, low 32 bits of the product.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32de6c(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduConnUpdateInd(uint32_t pdu, uint32_t unused, uint32_t len)
{
  uint32_t body, iv, timeout, lat;
  (void)unused;
  if (len == 0u) return 0x19u;
  body = pdu + 0xcu;
  (void)opencfw_em9305_packet_child_32de6c(body);
  if (B8(pdu + 5u) != 0xcu) return 0x19u;
  iv = H16(pdu + 0x10u);
  if ((uint16_t)(iv - 0xc81u) < 0xf385u) return 0x1eu;
  if (B8(body) == 0u || B8(body) >= (iv < 9u ? iv : 9u)) return 0x1eu;
  if (iv < H16(pdu + 0xeu)) return 0x1eu;
  timeout = H16(pdu + 0x14u);
  if ((uint16_t)(timeout - 0xc81u) < 0xf389u) return 0x1eu;
  lat = H16(pdu + 0x12u);
  if ((int32_t)((lat + 1u) * iv) >= (int32_t)(timeout << 2)) return 0x1eu;
  return lat < 500u ? 0u : 0x1eu;
}
