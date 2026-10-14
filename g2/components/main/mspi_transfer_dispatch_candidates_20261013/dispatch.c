/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78: MSPI transfer selector dispatcher.
 * Each selected branch has a separate locked-native/source oracle.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_transfer_basic_candidate(uint32_t, uint32_t,
                                                       const void *);
extern uint32_t g2_main_mspi_transfer_structured_candidate(uint32_t, uint32_t,
                                                            void *);
extern uint32_t g2_main_mspi_transfer_aux_candidate(uint32_t, uint32_t,
                                                     const void *);
extern uint32_t g2_main_mspi_transfer_control_candidate(uint32_t, uint32_t,
                                                         const void *);
extern uint32_t g2_main_mspi_transfer_mode24_candidate(uint32_t,
                                                        const void *);
extern uint32_t g2_main_mspi_transfer_mode26_candidate(uint32_t,
                                                        const void *);
extern uint32_t g2_main_mspi_transfer_queue_state_candidate(uint32_t,
                                                              uint32_t,
                                                              const void *);
extern uint32_t g2_main_mspi_transfer_queue_mode_candidate(uint32_t,
                                                             uint32_t,
                                                             const void *);
extern uint32_t g2_main_mspi_transfer_submit_candidate(uint32_t,
                                                         uint32_t,
                                                         const void *);
extern uint32_t g2_main_mspi_transfer_descriptor_candidate(uint32_t,
                                                             uint32_t,
                                                             const void *);

uint32_t g2_norflash_config_transfer_4c0f78(uint32_t controller,
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

    if (operation <= 13u)
        return g2_main_mspi_transfer_basic_candidate(
            controller, selector, configuration);
    if (operation <= 19u)
        return g2_main_mspi_transfer_structured_candidate(
            controller, selector, (void *)configuration);
    if (operation == 20u || operation == 25u || operation == 27u)
        return g2_main_mspi_transfer_aux_candidate(
            controller, selector, configuration);
    if (operation <= 23u || (operation >= 35u && operation <= 39u))
        return g2_main_mspi_transfer_control_candidate(
            controller, selector, configuration);
    if (operation == 24u)
        return g2_main_mspi_transfer_mode24_candidate(
            controller, configuration);
    if (operation == 26u)
        return g2_main_mspi_transfer_mode26_candidate(
            controller, configuration);
    if (operation == 28u || (operation >= 31u && operation <= 33u))
        return g2_main_mspi_transfer_queue_state_candidate(
            controller, selector, configuration);
    if (operation == 29u)
        return g2_main_mspi_transfer_queue_mode_candidate(
            controller, selector, configuration);
    if (operation == 30u)
        return g2_main_mspi_transfer_submit_candidate(
            controller, selector, configuration);
    if (operation == 34u)
        return g2_main_mspi_transfer_descriptor_candidate(
            controller, selector, configuration);
    return 6u; /* The locked native dispatcher rejects selector 40. */
}
