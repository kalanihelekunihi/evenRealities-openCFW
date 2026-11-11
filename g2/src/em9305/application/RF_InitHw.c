/* SPDX-License-Identifier: MIT
 * Stock 0x311d2c (RF_InitHw), g2-2.2.6.10 firmware_ble_em9305.bin. Waits for the ROM boot state, clears 0x805fe0 and 0xf04404, then programs a list of
 * 16-bit register writes from the table at 0x80fd4c (pointer) with its element count byte at 0x80fd50: each pair of halfwords is (index, value) and
 * the value is stored at 0xf04800 + ((index << 2) & 0x3fc); the number of pairs is ((count - 1) >> 1) + 1 (odd counts read one halfword past the
 * list, as stock does). It then sets 0xf04079 = 0, 0xf04078 = 16, 0xf04080 = 1, 0xf04080 = 2 and calls RF_IrqConfigure (0x311db8).
 * FLAGS: `incoming` is the caller's r0 left untouched by stock and passed on to ROM 0x103678 (RF_Init reaches this code with 0x3a in r0, so it is
 * probably not meaningful); ROM 0x103678 / 0x10361c are named by their existing controller_rom_boot_* wrappers; the registers at 0xf04078..0xf04080,
 * 0xf04404, 0xf04800.. and 0x805fe0 and the wait until bits 24..25 of 0xf03838 are both set are named by address only.
 */
#include <stdint.h>

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RW16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern uint32_t opencfw_em9305_controller_rom_boot_status(uint32_t incoming);
extern uint32_t opencfw_em9305_controller_rom_boot_ready(uint32_t status);
extern void opencfw_em9305_stock_311db8(void);

void opencfw_em9305_stock_311d2c(uint32_t incoming)
{
  uint32_t status = opencfw_em9305_controller_rom_boot_status(incoming);
  if ((status & 0x300u) != 0u && opencfw_em9305_controller_rom_boot_ready(status) == 0u) {
    while ((RW32(0xf03838u) & 0x3000000u) != 0x3000000u) {
    }
  }
  RW32(0x805fe0u) = 0u;
  RW32(0xf04404u) = 0u;
  uint32_t count = RB8(0x80fd50u);
  if (count != 0u) {
    const uint16_t *entry = (const uint16_t *)(uintptr_t)RW32(0x80fd4cu);
    uint32_t pairs = ((count - 1u) >> 1) + 1u;
    do {
      uint32_t index = entry[0];
      uint16_t value = entry[1];
      entry += 2;
      RW16(0xf04800u + ((index << 2) & 0x3fcu)) = value;
    } while (--pairs != 0u);
  }
  RB8(0xf04079u) = 0u;
  RB8(0xf04078u) = 16u;
  RW32(0xf04080u) = 1u;
  RW32(0xf04080u) = 2u;
  opencfw_em9305_stock_311db8();
}
