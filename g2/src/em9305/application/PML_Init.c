/* SPDX-License-Identifier: MIT
 * Stock 0x30f4b0 (PML_Init), g2-2.2.6.10 firmware_ble_em9305.bin. Initialises the power-management record whose pointer is at (uintptr_t)&em9305_ram_80fb8c from the
 * parameter record at 0x80fb80 (+0x14/+0x18 words, +0x1e mode byte, +0x1f flag byte, +0x2e u16 factor, +0x34/+0x38 words; byte ((uintptr_t)&em9305_ram_80fb8c + 0x32u) is the
 * argument of the final ROM call), then runs the controller start-up helpers. Field names are not recovered (offsets only).
 * FLAGS: the product `(word +0x34 + word +0x38) * (u16 factor)` is the low 32 bits of the ARCv2 DSP mpywhul (settled from firmware usage, unproven on
 * silicon); `xbfu r0,r0,3` on register 0xf00404 is kept as inline asm (bit field position/width encoding not confirmed; the stored byte is bit 3,
 * as in PML_UseLfXtalClk); the stale-register arguments to timer_reset/finish_init (previous return values) are modelled as passed values;
 * 0xf00404 and byte +0x25 of the record are named by address only.
 */
#include <stdint.h>
#include "em9305_ram.h"

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RW16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern uint32_t opencfw_em9305_controller_configure_mode(uint32_t mode);
extern uint32_t opencfw_em9305_controller_prepare_timer(void);
extern uint32_t opencfw_em9305_controller_timer_reset(uint32_t incoming);
extern uint32_t opencfw_em9305_controller_finish_init(uint32_t incoming);
extern uint32_t opencfw_em9305_controller_rom_init(uint32_t value);

uint32_t opencfw_em9305_stock_30f4b0(void)
{
  uint32_t c = RW32((uintptr_t)&em9305_ram_80fb8c);
  RW32(c + 4u) = (RW32(((uintptr_t)&em9305_ram_80fb8c + 0x28u)) + RW32(((uintptr_t)&em9305_ram_80fb8c + 0x2cu))) * (uint32_t)RW16(((uintptr_t)&em9305_ram_80fb8c + 0x22u));
  RW32(c + 8u) = RW32(((uintptr_t)&em9305_ram_80fb8c + 0x8u));
  RW32(c + 12u) = RW32(((uintptr_t)&em9305_ram_80fb8c + 0xcu));
  RW32(c + 20u) = 0u;
  RW32(c + 24u) = 0u;
  RB8(c + 38u) = RB8(((uintptr_t)&em9305_ram_80fb8c + 0x13u));
  RW32(c + 28u) = 0u;
  RW32(c + 32u) = 0u;
  RB8(c + 39u) = 0u;
  RB8(c + 40u) = 0u;
  RW32(c + 16u) = 0u;
  RB8(c + 41u) = 0u;
  RB8(c + 42u) = 1u;
  RB8(c + 44u) = 0u;
  RB8(c + 45u) = 0u;
  RB8(c + 43u) = 0u;
  if (RB8(((uintptr_t)&em9305_ram_80fb8c + 0x12u)) != 0u) {
    RB8(c + 36u) = 1u;
    (void)opencfw_em9305_controller_configure_mode(RB8(((uintptr_t)&em9305_ram_80fb8c + 0x12u)));
  } else {
    RB8(c + 36u) = 0u;
  }
  uint32_t field = RW32(0xf00404u);
  field=((uint32_t)field>>3u)&0x1u;
  RB8(c + 37u) = (uint8_t)field;
  uint32_t value = RB8(c + 38u);
  if (value == 0u) value = opencfw_em9305_controller_prepare_timer();
  value = opencfw_em9305_controller_timer_reset(value);
  (void)opencfw_em9305_controller_finish_init(value);
  return opencfw_em9305_controller_rom_init(RB8(((uintptr_t)&em9305_ram_80fb8c + 0x32u)));
}
