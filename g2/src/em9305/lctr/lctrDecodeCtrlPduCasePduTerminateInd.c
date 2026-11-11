/* SPDX-License-Identifier: MIT
 * Stock 0x3196ec lctrDecodeCtrlPduCasePduTerminateInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). FLAG: name from the opcode position (0x02 LL_TERMINATE_IND) in the stock dispatch table 0x334d0c; the stock image names the 0x3196ec block 'unnamed'. Copies the one-byte parameter src[1] to pdu+0xc and accepts packet type 2. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduTerminateInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)len;
  B8(pdu + 0xcu) = B8(src + 1u);
  return B8(pdu + 5u) == 2u ? 0u : 0x19u;
}
