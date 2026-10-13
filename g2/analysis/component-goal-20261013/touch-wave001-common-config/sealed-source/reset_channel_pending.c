/* SPDX-License-Identifier: MIT
 * LP channel at RAM 0x2000082c, reset-copy ROM 0xb8f8.
 * ABI: Infineon CapSense v6 cy_stc_capsense_channel_config_t (LP).
 * Common configuration ROM 0xb2a8+8 points here; native preparation reads
 * channel+0 as MSCLP and channel+4 as the driver context.
 * Driver lock ABI: pinned PDL 69bb46becb33da0215576d6d22f6b225165d4c28.
 * Bounded oracle placement is not final firmware placement.
 */
#include <stdint.h>
#include <stddef.h>
#include "reset_pin_config.h"
struct touch_msclp_driver_context { uint32_t lock_key; };
struct touch_shield_electrode_config {
    const struct touch_pin_config *pins;
    uint8_t type,count;
};
_Static_assert(sizeof(struct touch_shield_electrode_config)==8,"LP electrode ABI");
struct touch_msclp_driver_context touch_msclp_context_ram_20000cc8
    __attribute__((section(".touch_bss.msclp_context"),used));
const struct touch_pin_config touch_shield_pins_rom_b33c[2]
    __attribute__((section(".touch_rom.shield_pins"),used)) = {
    {(volatile uint32_t *)(uintptr_t)0x40040200u,0u,7u},
    {(volatile uint32_t *)(uintptr_t)0x40040200u,1u,8u},
};
const struct touch_shield_electrode_config touch_shield_config_rom_b32c[2]
    __attribute__((section(".touch_rom.shield_electrodes"),used)) = {
    {&touch_shield_pins_rom_b33c[0],0u,1u},
    {&touch_shield_pins_rom_b33c[1],0u,1u},
};
typedef struct touch_reset_lp_channel {
    volatile uint32_t *hardware;
    struct touch_msclp_driver_context *context;
    volatile uint32_t *cmod1_port;
    uint8_t cmod1_pin;
    volatile uint32_t *cmod2_port;
    uint8_t cmod2_pin;
    const struct touch_shield_electrode_config *shield;
} touch_reset_lp_channel;
_Static_assert(sizeof(touch_reset_lp_channel)==28,"LP channel ABI");
_Static_assert(offsetof(touch_reset_lp_channel,cmod2_port)==16,"Cmod2 ABI");
_Static_assert(offsetof(touch_reset_lp_channel,shield)==24,"shield ABI");
touch_reset_lp_channel touch_reset_channel
    __attribute__((section(".touch_init.pending_channel"),used)) = {
    .hardware=(volatile uint32_t *)(uintptr_t)0x40290000u,
    .context=&touch_msclp_context_ram_20000cc8,
    .cmod1_port=(volatile uint32_t *)(uintptr_t)0x40040400u,
    .cmod1_pin=2u,
    .cmod2_port=(volatile uint32_t *)(uintptr_t)0x40040400u,
    .cmod2_pin=3u,
    .shield=&touch_shield_config_rom_b32c[0],
};
