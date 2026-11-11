/* SPDX-License-Identifier: MIT
 * Stock 0x30299c (AOAD_Init), g2-2.2.6.10 firmware_ble_em9305.bin. Clears the byte at 0x8019f1, then, when the enable byte at 0x80fb60 is non-zero,
 * copies the three words at 0x80fb48..0x80fb50 to 0xf04c04/0xf04c08/0xf04c0c and, for each of the 12 flag bytes at 0x80fb54..0x80fb5f that is
 * non-zero (index i), clears bit i in 0xf0340c, 0xf03408 and 0xf03400, sets bit i in 0xf03404 and calls ROM 0x102b00(i, 13). The register and record
 * meanings are not recovered (named by address only).
 * FLAGS: ROM 0x102b00 is named by address only (its two arguments are (index, 0xd)); stock leaves a stale r0 on return, treated as void.
 */
#include <stdint.h>

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern void em9305_rom_102b00(uint32_t index, uint32_t value);

void opencfw_em9305_stock_30299c(void)
{
  uint32_t enabled = RB8(0x80fb60u);
  RB8(0x8019f1u) = 0u;
  if (enabled == 0u) return;
  RW32(0xf04c04u) = RW32(0x80fb48u);
  RW32(0xf04c08u) = RW32(0x80fb4cu);
  RW32(0xf04c0cu) = RW32(0x80fb50u);
  for (uint32_t i = 0u; i < 12u; i++) {
    if (RB8(0x80fb54u + i) != 0u) {
      RW32(0xf0340cu) &= ~(1u << i);
      RW32(0xf03408u) &= ~(1u << i);
      RW32(0xf03400u) &= ~(1u << i);
      RW32(0xf03404u) |= (1u << i);
      em9305_rom_102b00(i, 0xdu);
    }
  }
}
