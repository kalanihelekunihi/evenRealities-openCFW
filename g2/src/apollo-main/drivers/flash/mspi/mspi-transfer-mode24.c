/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 24: mode byte and transmit-width register.
 * The full selector dispatcher remains gated.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_mode_update_4c0644(uint32_t);

uint32_t g2_main_mspi_transfer_mode24_candidate(uint32_t controller,
                                                  const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (configuration == 0)
        return 6u;
    *(volatile uint8_t *)(uintptr_t)(controller + 11u) =
        *(const uint8_t *)configuration;
    (void)g2_main_mspi_mode_update_4c0644(controller);
    return 0u;
}
