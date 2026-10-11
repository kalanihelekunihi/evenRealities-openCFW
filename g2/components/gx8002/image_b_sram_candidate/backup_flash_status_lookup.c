/* SPDX-License-Identifier: MIT
 * Image-B 0x10006f04: match a protection status entry for the probed chip.
 * The descriptor, chip metadata and entry table are separate SRAM data.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);

static uint32_t read_word(const volatile uint8_t *p)
{
    return *(const volatile uint32_t *)(const void *)p;
}

uint32_t gx8002_image_b_flash_status_lookup_10006f04(void)
{
    volatile const uint8_t *const descriptor =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20016d60);
    volatile const uint8_t *chip =
        (volatile const uint8_t *)(uintptr_t)read_word(descriptor + 0x0cu);
    volatile const uint8_t *configuration =
        (volatile const uint8_t *)(uintptr_t)read_word(chip + 0x10u);
    if (configuration == (volatile const uint8_t *)0 ||
        read_word(configuration) == 0u) return UINT32_MAX;

    uint8_t first_status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &first_status, 1u);
    } while ((first_status & 1u) != 0u);
    uint16_t chip_kind = *(const volatile uint16_t *)(const void *)(chip + 6u);
    if (chip_kind != 0x5eu && chip_kind != 0x85u) return UINT32_MAX;

    (void)gx8002_image_b_flash_read_10006c30(5u, &first_status, 1u);
    uint8_t second_status;
    (void)gx8002_image_b_flash_read_10006c30(0x35u, &second_status, 1u);
    chip = (volatile const uint8_t *)(uintptr_t)read_word(descriptor + 0x0cu);
    configuration = (volatile const uint8_t *)(uintptr_t)read_word(chip + 0x10u);
    uint32_t count = read_word(configuration + 4u);
    volatile const uint8_t *entry =
        (volatile const uint8_t *)(uintptr_t)read_word(configuration);
    for (uint32_t i = 0u; i < count; ++i, entry += 8u) {
        if (entry[0] == (uint8_t)(entry[1] & first_status) &&
            entry[2] == (uint8_t)(entry[3] & second_status))
            return read_word(entry + 4u);
    }
    return UINT32_MAX;
}
