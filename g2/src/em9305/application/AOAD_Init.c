/* SPDX-License-Identifier: MIT
 * Stock 0x30299c (AOAD_Init), g2-2.2.6.10 firmware_ble_em9305.bin. Clears the byte at ((uintptr_t)&em9305_ram_8019e8 + 0x9u), then, when the enable byte at ((uintptr_t)&em9305_ram_80fb48 + 0x18u) is non-zero,
 * copies the three words at (uintptr_t)&em9305_ram_80fb48..((uintptr_t)&em9305_ram_80fb48 + 0x8u) to 0xf04c04/0xf04c08/0xf04c0c and, for each of the 12 flag bytes at ((uintptr_t)&em9305_ram_80fb48 + 0xcu)..((uintptr_t)&em9305_ram_80fb48 + 0x17u) that is
 * non-zero (index i), clears bit i in 0xf0340c, 0xf03408 and 0xf03400, sets bit i in 0xf03404 and calls ROM 0x102b00(i, 13). The register and record
 * meanings are not recovered (named by address only).
 * FLAGS: ROM 0x102b00 is named by address only (its two arguments are (index, 0xd)); stock leaves a stale r0 on return, treated as void.
 */
#include <stdint.h>
#include "em9305_ram.h"

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern void em9305_rom_102b00(uint32_t index, uint32_t value);

void opencfw_em9305_stock_30299c(void)
{
  uint32_t enabled = RB8(((uintptr_t)&em9305_ram_80fb48 + 0x18u));
  RB8(((uintptr_t)&em9305_ram_8019e8 + 0x9u)) = 0u;
  if (enabled == 0u) return;
  RW32(0xf04c04u) = RW32((uintptr_t)&em9305_ram_80fb48);
  RW32(0xf04c08u) = RW32(((uintptr_t)&em9305_ram_80fb48 + 0x4u));
  RW32(0xf04c0cu) = RW32(((uintptr_t)&em9305_ram_80fb48 + 0x8u));
  for (uint32_t i = 0u; i < 12u; i++) {
    if (RB8(((uintptr_t)&em9305_ram_80fb48 + 0xcu) + i) != 0u) {
      RW32(0xf0340cu) &= ~(1u << i);
      RW32(0xf03408u) &= ~(1u << i);
      RW32(0xf03400u) &= ~(1u << i);
      RW32(0xf03404u) |= (1u << i);
      em9305_rom_102b00(i, 0xdu);
    }
  }
}
