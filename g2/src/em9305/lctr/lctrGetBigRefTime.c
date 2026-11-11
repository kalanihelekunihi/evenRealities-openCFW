/* SPDX-License-Identifier: MIT
 * Stock 0x31afd4 lctrGetBigRefTime (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified
 * against it in the QEMU-ARC harness (.waves/w28). Looks up the BIG context table entry for handle `idx` (table base at 0x805c3c, 0x200-byte
 * entries, handles start at 7) and, when its state byte (+1) is 1, returns the low word of its 64-bit reference time (+0x130) and stores the
 * high word (+0x134) through `hi` when non-NULL; otherwise returns 0 and leaves *hi untouched. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrGetBigRefTime(uint32_t idx, uint32_t *hi)
{
  uint32_t ent = W32(0x805c3cu) + ((idx - 7u) << 9);
  if (B8(ent + 1u) != 1u) return 0u;
  if (hi != 0) *hi = W32(ent + 0x134u);
  return W32(ent + 0x130u);
}
