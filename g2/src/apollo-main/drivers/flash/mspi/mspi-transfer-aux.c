/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selectors 20, 25 and 27. Full transfer dispatcher gated.
 */
#include <stdint.h>

extern void audio_delay_us_selected(uint32_t);
extern uint32_t g2_main_mspi_configure_aux_4bfed6(uint32_t);
extern uint64_t g2_main_mspi_queue_terminate_4bfd6e(uint32_t, uint32_t,
                                                      uint32_t, uint32_t);

uint32_t g2_main_mspi_transfer_aux_candidate(uint32_t controller,
                                              uint32_t selector,
                                              const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint32_t operation = selector & 0xffu;
    if (operation > 40u) return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (operation != 20u && operation != 25u && operation != 27u)
        return 6u;
    if (operation == 27u)
        return (uint32_t)g2_main_mspi_queue_terminate_4bfd6e(
            controller, selector, (uint32_t)(uintptr_t)configuration, 0u);
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    if (operation == 20u) {
        audio_delay_us_selected(
            *(const volatile uint32_t *)(uintptr_t)(controller + 0x8ccu));
        volatile uint32_t *const flags =
            (volatile uint32_t *)(uintptr_t)
            (UINT32_C(0x40060090) + module * 0x1000u);
        *flags &= UINT32_C(0xfffffffe);
        return 0u;
    }
    if (configuration == 0) return 6u;
    const uint8_t choice = *(const uint8_t *)configuration;
    if ((module == 1u || module == 2u) &&
        (choice == 10u || choice == 11u))
        return 5u;
    *(volatile uint8_t *)(uintptr_t)(controller + 10u) = choice;
    (void)g2_main_mspi_configure_aux_4bfed6(controller);
    return 0u;
}
