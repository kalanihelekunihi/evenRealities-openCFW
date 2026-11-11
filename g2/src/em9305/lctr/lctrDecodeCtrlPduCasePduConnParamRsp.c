/* SPDX-License-Identifier: MIT
 * Stock 0x31935c lctrDecodeCtrlPduCasePduConnParamRsp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and
 * verified against it in the QEMU-ARC harness (.waves/w28). A one-byte-length PDU is rejected (0x19); anything else is decoded exactly like
 * a connection-parameter request. Field names are not recovered (offsets only).
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamReq(uint32_t pdu, uint32_t src, uint32_t len);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamRsp(uint32_t pdu, uint32_t src, uint32_t len)
{
  if (len == 1u) return 0x19u;
  return opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamReq(pdu, src, len);
}
