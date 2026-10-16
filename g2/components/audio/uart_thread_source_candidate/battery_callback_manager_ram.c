/* Observed Apollo Main callback-manager cells; first 12 bytes accessed. */
#include <stdint.h>

uint8_t audio_charge_callback_manager[12]
    __attribute__((section(".bss.opencfw.callback.charge"), aligned(4), used));
uint8_t audio_ring_battery_callback_manager[12]
    __attribute__((section(".bss.opencfw.callback.ring_battery"), aligned(4), used));

_Static_assert(sizeof(audio_charge_callback_manager) == 12u, "charge manager extent");
_Static_assert(sizeof(audio_ring_battery_callback_manager) == 12u,
               "ring battery manager extent");
