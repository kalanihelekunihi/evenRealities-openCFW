/* SPDX-License-Identifier: MIT
 * Image-B 0x10006fec: apply a protection status-table entry.
 * Table records and chip metadata remain separately initialized SRAM data.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);
extern int32_t gx8002_image_b_flash_program_command_10006d34(
    const uint8_t *source, uint32_t length, uint32_t mode);
extern uint32_t gx8002_image_b_flash_status_lookup_10006f04(void);

static uint32_t word_at(const volatile uint8_t *p)
{
    return *(const volatile uint32_t *)(const void *)p;
}

uint32_t gx8002_image_b_flash_status_apply_10006fec(
    uint32_t requested, uint32_t *matched_value)
{
    volatile const uint8_t *const descriptor =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20016d60);
    volatile const uint8_t *chip =
        (volatile const uint8_t *)(uintptr_t)word_at(descriptor + 0x0cu);
    *matched_value = 0u;
    volatile const uint8_t *config =
        (volatile const uint8_t *)(uintptr_t)word_at(chip + 0x10u);
    if (config == (volatile const uint8_t *)0 || word_at(config) == 0u)
        return requested == 0u ? 0u : UINT32_MAX;

    uint32_t chip_id = word_at(chip + 4u) >> 16;
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);

    chip = (volatile const uint8_t *)(uintptr_t)word_at(descriptor + 0x0cu);
    config = (volatile const uint8_t *)(uintptr_t)word_at(chip + 0x10u);
    uint32_t count = word_at(config + 4u);
    volatile const uint8_t *record =
        (volatile const uint8_t *)(uintptr_t)word_at(config);
    uint8_t set_low = 0u, clear_low = 0u;
    uint8_t set_high = 0u, clear_high = 0u;
    if (count != 0u && word_at(record + 4u) <= requested) {
        for (uint32_t i = 0u; i < count; ++i) {
            set_low = record[0];
            clear_low = record[1];
            set_high = record[2];
            clear_high = record[3];
            if (i + 1u == count || word_at(record + 12u) > requested) break;
            record += 8u;
        }
    }
    if (chip_id != 0x5eu && chip_id != 0x85u) return UINT32_MAX;

    uint8_t new_status[2];
    (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    new_status[0] = (uint8_t)(set_low | (status & (uint8_t)~clear_low));
    (void)gx8002_image_b_flash_read_10006c30(0x35u, &status, 1u);
    new_status[1] = (uint8_t)(set_high | (status & (uint8_t)~clear_high));
    do {
        (void)gx8002_image_b_flash_program_command_10006d34(new_status, 2u, 1u);
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    uint32_t match = gx8002_image_b_flash_status_lookup_10006f04();
    if (match == UINT32_MAX) return UINT32_MAX;
    *matched_value = match;
    return 0u;
}
