/* SPDX-License-Identifier: MIT
 * Source-owned generated CapSense pin records at stock ROM 0xb34c..0xb373.
 * Record identity and field layout: pinned CapSense v6 LP structure header;
 * values: official G2 2.3.0.24 touch ROM and common config pointer table.
 */
#include "reset_pin_config.h"
const struct touch_pin_config touch_generated_pin_config[5]
 __attribute__((section(".touch_rom.pin_config"),used)) = {
  {(volatile uint32_t *)(uintptr_t)0x40040000u,0u,0u},
  {(volatile uint32_t *)(uintptr_t)0x40040000u,1u,1u},
  {(volatile uint32_t *)(uintptr_t)0x40040000u,2u,2u},
  {(volatile uint32_t *)(uintptr_t)0x40040000u,3u,3u},
  {(volatile uint32_t *)(uintptr_t)0x40040200u,4u,11u},
};
