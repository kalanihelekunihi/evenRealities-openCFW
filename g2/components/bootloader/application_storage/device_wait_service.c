/* SPDX-License-Identifier: MIT
 * Source reconstruction of stock INFO-space dispatch at 0x4213e6.
 * Addresses, word counts, and selector meanings are corroborated by the
 * pinned Apollo510 SDK 5.1 INFO HAL declarations (see worker report).
 */
#include "device_wait_service.h"

#define INFO_SOURCE_STATE (*(volatile uint32_t *)(uintptr_t)0x400201bcu)
#define INFO_READY_STATE  (*(volatile uint32_t *)(uintptr_t)0x40021008u)

extern uint32_t opencfw_boot_info_rom_read(uint32_t address,
                                           volatile uint32_t *destination,
                                           uint32_t word_count);

static uint32_t adjust_info1_word_offset(uint32_t word_offset)
{
    return word_offset < 0x200u ? word_offset : word_offset + 0x280u;
}

uint32_t opencfw_boot_info_read_dispatch(uint32_t info_space,
                                         uint32_t word_offset,
                                         uint32_t word_count,
                                         volatile uint32_t *destination)
{
    const uint32_t source_state = INFO_SOURCE_STATE;
    const uint32_t ready_state = INFO_READY_STATE;
    const uint32_t current_info0_is_otp = (source_state >> 4) & 1u;
    const uint32_t current_info1_is_otp = (source_state >> 3) & 1u;
    const uint32_t otp_ready = (ready_state >> 27) & 1u;
    const uint8_t selected_space = (uint8_t)info_space;
    uint32_t maximum_words;
    uint32_t info_address;

    if (destination == 0)
        return 6u;

    switch (selected_space) {
    case 0u: maximum_words = current_info0_is_otp ? 0x40u : 0x200u; break;
    case 1u: maximum_words = current_info1_is_otp ? 0x2c0u : 0x600u; break;
    case 2u: maximum_words = 0x40u; break;
    case 3u: maximum_words = 0x2c0u; break;
    case 4u: maximum_words = 0x200u; break;
    case 5u: maximum_words = 0x600u; break;
    default: return 6u;
    }

    if (word_offset + word_count > maximum_words)
        return 5u;

    switch (selected_space) {
    case 0u:
        if (current_info0_is_otp != 0u) {
            if (otp_ready == 0u)
                return 9u;
            info_address = 0x42004000u + word_offset * 4u;
        } else {
            info_address = 0x42000000u + word_offset * 4u;
        }
        break;
    case 1u:
        if (current_info1_is_otp != 0u) {
            if (otp_ready == 0u)
                return 9u;
            info_address = 0x42006000u + word_offset * 4u;
        } else {
            info_address = 0x42002000u + adjust_info1_word_offset(word_offset) * 4u;
        }
        break;
    case 3u:
        if (otp_ready == 0u)
            return 9u;
        info_address = 0x42006000u + word_offset * 4u;
        break;
    case 2u:
        if (otp_ready == 0u)
            return 9u;
        info_address = 0x42004000u + word_offset * 4u;
        break;
    case 4u:
        info_address = 0x42000000u + word_offset * 4u;
        break;
    case 5u:
        info_address = 0x42002000u + word_offset * 4u;
        break;
    default:
        return 6u;
    }

    (void)opencfw_boot_info_rom_read(info_address, destination, word_count);
    return 0u;
}

/* Kept for callers in the frozen mode-wait integration; this is an INFO read. */
uint32_t opencfw_boot_device_wait_service(uint32_t info_space,
                                          uint32_t word_offset,
                                          uint32_t word_count,
                                          volatile uint32_t *destination)
{
    return opencfw_boot_info_read_dispatch(info_space, word_offset,
                                           word_count, destination);
}
