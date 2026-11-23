/* SPDX-License-Identifier: MIT
 * Stock 0x3292f4 lctrSlvBisTxCompletionInterleaved (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted
 * from the lowered ARC asm. Field names are not recovered (offsets only); G=&em9305_ram_80542c is the 28-byte TX cursor
 * {u32 key@+0; u8 idx@+4; ...; u32 ts@+0x10; u32 ptr@+0x14; u32 flag@+0x18}.
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_dispatch_child_3173ac(uint32_t big, uint32_t cur);
extern void opencfw_em9305_auxiliary_signal_304394(void);
extern void opencfw_em9305_lctrSlvBisTxControl(uint32_t big);
extern void opencfw_em9305_lctrSlvBisTxData(uint32_t big);

void opencfw_em9305_lctrSlvBisTxCompletionInterleaved(uint32_t ctx, uint32_t kind)
{
  struct { uint32_t key; uint8_t idx; } tmp;
  uint32_t big, ptr;

  if (kind == 1u) goto signal;
  big = W32(ctx + 0x24u);
  if (em9305_ram_80542c.u8_805430[0] >= B8(big + 0x19u)) goto signal;
  if (opencfw_em9305_dispatch_child_3173ac(big, (uint32_t)(uintptr_t)&em9305_ram_80542c) == 0u) {
    if (em9305_ram_80542c.u32_805444 == 0u) goto signal;
    opencfw_em9305_lctrSlvBisTxControl(big);
    return;
  }
  tmp.key = em9305_ram_80542c.u32_80542c;
  tmp.idx = em9305_ram_80542c.u8_805430[0];
  if (opencfw_em9305_dispatch_child_3173ac(big, (uint32_t)(uintptr_t)&tmp) != 0u)
    ptr = W32(big + ((uint32_t)(*(volatile uint8_t *)&tmp.key) << 2) + 0x38u) + 0xb0u;
  else
    ptr = (em9305_ram_80542c.u32_805444 != 0u) ? big + 0x198u : 0u;
  em9305_ram_80542c.u32_805440 = ptr;
  em9305_ram_80542c.u32_80543c = em9305_ram_80542c.u32_80543c + W32(big + 0xcu);
  opencfw_em9305_lctrSlvBisTxData(big);
  return;
signal:
  opencfw_em9305_auxiliary_signal_304394();
}
