/* SPDX-License-Identifier: MIT
 * Stock 0x313880 (System_Save) and 0x3137fc (System_Restore), g2-2.2.6.10 firmware_ble_em9305.bin. A save record lives at the address held in the pointer word at
 * em9305_ram_80fd2c.u32_80fd80 (re-read before every access, as stock does; after e1 this is em9305_ram_801250). Save copies 0xf03800 & 1 to record word 0x4c, the words at 0xf03804..0xf0382c (11 words) to record
 * offsets 4..0x2c, then 0xf03830 -> 0x30, 0xf03834 -> 0x34 and 0xf03844 -> 0x44. Restore passes record word 0x4c to the sleep ROM prepare routine (0x103ab4,
 * via opencfw_em9305_sleep_rom_prepare) and writes the same register words back (record 4..0x2c -> 0xf03804.., 0x30 -> 0xf03830, 0x34 -> 0xf03834,
 * 0x44 -> 0xf03844). Register 0xf03800 itself is not rewritten directly, only through the ROM routine's argument. The registers and record fields are named
 * by address only (meaning not recovered).
 * FLAGS: stock Save leaves the record pointer in r0 and Restore leaves record word 0x44 in r0 (both treated as void, return values are not used by
 * callers seen); the record pointer is not allocated here (stock does the same).
 */
#include <stdint.h>
#include "em9305_ram.h"

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define REC (*(uint32_t * volatile *)&em9305_ram_80fd2c.u32_80fd80)

extern uint32_t opencfw_em9305_sleep_rom_prepare(uint32_t a);

void opencfw_em9305_stock_313880(void)
{
  REC[0x4c / 4] = RW32(0xf03800u) & 1u;
  for (uint32_t i = 1u; i <= 11u; i++) REC[i] = RW32(0xf03800u + i * 4u);
  REC[0x30 / 4] = RW32(0xf03830u);
  REC[0x34 / 4] = RW32(0xf03834u);
  REC[0x44 / 4] = RW32(0xf03844u);
}

void opencfw_em9305_stock_3137fc(void)
{
  (void)opencfw_em9305_sleep_rom_prepare(REC[0x4c / 4]);
  for (uint32_t i = 1u; i <= 11u; i++) RW32(0xf03800u + i * 4u) = REC[i];
  RW32(0xf03830u) = REC[0x30 / 4];
  RW32(0xf03834u) = REC[0x34 / 4];
  RW32(0xf03844u) = REC[0x44 / 4];
}
