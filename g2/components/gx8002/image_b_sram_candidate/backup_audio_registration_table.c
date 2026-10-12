/* SPDX-License-Identifier: MIT
 * Image-B 0x1000b430: 16-entry, 28-byte callback registration table at
 * 0x2002cf30. Native code clears every matching key before inserting at
 * the first free entry, including the special zero-key behavior.
 */
#include <stdint.h>

#define REGISTRATION_BASE ((volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cf30))

static uint32_t read_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(const volatile uint32_t *)(const volatile void *)(base + offset);
}

static void write_word(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)(base + offset) = value;
}

int32_t gx8002_image_b_audio_registration_table_at_1000b430(
    volatile uint8_t *table, const uint8_t *entry)
{
    const volatile uint8_t *source = (const volatile uint8_t *)entry;
    uint32_t key = read_word(source, 4u);
    for (uint32_t index = 0u; index < 16u; ++index) {
        volatile uint8_t *slot = table + index * 28u;
        if (read_word(slot, 4u) == key) {
            write_word(slot, 4u, 0u);
            slot[0] = 0xffu;
            write_word(slot, 8u, 0u);
            write_word(slot, 12u, 0u);
            write_word(slot, 16u, 0u);
            write_word(slot, 24u, 0u);
            write_word(slot, 20u, 0u);
        }
    }
    uint32_t selected = 0u;
    if (read_word(table, 4u) != 0u) {
        for (selected = 1u; selected < 16u; ++selected) {
            if (read_word(table + selected * 28u, 4u) == 0u)
                break;
        }
        if (selected == 16u) return -1;
    }
    volatile uint8_t *slot = table + selected * 28u;
    write_word(slot, 4u, key);
    slot[0] = source[0];
    write_word(slot, 8u, read_word(source, 8u));
    write_word(slot, 12u, read_word(source, 12u));
    write_word(slot, 16u, read_word(source, 16u));
    write_word(slot, 24u, read_word(source, 24u));
    write_word(slot, 20u, read_word(source, 20u));
    return 0;
}

int32_t gx8002_image_b_audio_registration_table_1000b430(
    const uint8_t *entry)
{
    return gx8002_image_b_audio_registration_table_at_1000b430(
        REGISTRATION_BASE, entry);
}
