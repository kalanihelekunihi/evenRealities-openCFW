/* SPDX-License-Identifier: MIT
 * Stock 0x329368 lctrSlvBisTxCompletionSequential (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted
 * from the lowered ARC asm. Field names are not recovered (offsets only); G=0x80542c is the TX cursor
 * {u32 key; u8 idx; ...; u32 ptr@+0x14; u32 ts@+0x10; u32 flag@+0x18}.
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define LCTR_SLV_BIG_CUR 0x80542cu
extern uint32_t opencfw_em9305_dispatch_child_317418(uint32_t big, uint32_t cur);
extern void opencfw_em9305_auxiliary_signal_304394(void);
extern void opencfw_em9305_lctrSlvBisTxControl(uint32_t big);
extern void opencfw_em9305_lctrSlvBisTxData(uint32_t big);

void opencfw_em9305_lctrSlvBisTxCompletionSequential(uint32_t ctx, uint32_t kind)
{
  struct { uint32_t key; uint8_t idx; } tmp;
  uint32_t big, ptr;

  if (kind == 1u) goto signal;
  big = W32(ctx + 0x24u);
  if (B8(LCTR_SLV_BIG_CUR) >= B8(big + 0x34u)) goto signal;
  if (opencfw_em9305_dispatch_child_317418(big, LCTR_SLV_BIG_CUR) == 0u) {
    if (W32(LCTR_SLV_BIG_CUR + 0x18u) == 0u) goto signal;
    opencfw_em9305_lctrSlvBisTxControl(big);
    return;
  }
  tmp.key = W32(LCTR_SLV_BIG_CUR);
  tmp.idx = B8(LCTR_SLV_BIG_CUR + 4u);
  if (opencfw_em9305_dispatch_child_317418(big, (uint32_t)(uintptr_t)&tmp) != 0u)
    ptr = W32(big + ((uint32_t)(*(volatile uint8_t *)&tmp.key) << 2) + 0x38u) + 0xb0u;
  else
    ptr = (W32(LCTR_SLV_BIG_CUR + 0x18u) != 0u) ? big + 0x198u : 0u;
  W32(LCTR_SLV_BIG_CUR + 0x14u) = ptr;
  W32(LCTR_SLV_BIG_CUR + 0x10u) = W32(LCTR_SLV_BIG_CUR + 0x10u) + W32(big + 0x30u);
  opencfw_em9305_lctrSlvBisTxData(big);
  return;
signal:
  opencfw_em9305_auxiliary_signal_304394();
}
