/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 16: packed MSPI transfer format registers.
 * This branch is source-owned; the full selector dispatcher remains gated.
 */
#include <stdint.h>

static void field(volatile uint32_t *register_word,
                  uint32_t clear_mask, uint32_t value)
{
    *register_word = (*register_word & clear_mask) | value;
}

uint32_t g2_main_mspi_transfer_mode16_candidate(uint32_t controller,
                                                  const void *configuration)
{
    const volatile uint8_t *const handle =
        (const volatile uint8_t *)(uintptr_t)controller;
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    if (handle[8] == 0u)
        return 7u;
    if (configuration == 0)
        return 6u;

    const uint8_t *const cfg = (const uint8_t *)configuration;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uintptr_t base = UINT32_C(0x40060000) + module * 0x1000u;
    volatile uint32_t *const format =
        (volatile uint32_t *)(base + 0x84u);
    volatile uint32_t *const control =
        (volatile uint32_t *)(base + 0x88u);
    volatile uint32_t *const options =
        (volatile uint32_t *)(base + 0x90u);
    volatile uint32_t *const auxiliary =
        (volatile uint32_t *)(base + 0xa8u);

    field(format, UINT32_C(0xfeffffff), (uint32_t)(cfg[0] & 1u) << 24);
    field(format, UINT32_C(0xff7fffff), (uint32_t)(cfg[1] & 1u) << 23);
    field(format, UINT32_C(0xffbfffff), (uint32_t)(cfg[2] & 1u) << 22);
    field(format, UINT32_C(0xffffc0ff), (uint32_t)(cfg[5] & 0x3fu) << 8);
    field(options, UINT32_C(0xfff03fff), (uint32_t)(cfg[5] & 0x3fu) << 14);
    field(control, UINT32_C(0xfffffc1f), (uint32_t)(cfg[3] & 0x1fu) << 5);
    field(control, UINT32_C(0xffff83ff), (uint32_t)(cfg[4] & 0x1fu) << 10);
    field(auxiliary, UINT32_C(0xfffffffe),
          (uint32_t)((cfg[4] & 0x3fu) >> 5));
    return 0u;
}
