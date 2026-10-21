/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 26: serial clock and MSPI mode transition.
 * This branch is source-owned; the full selector dispatcher remains gated.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_clock_route_4c0758(uint32_t, uint32_t,
                                                   uint32_t, uint32_t);
extern uint32_t g2_main_mspi_clock_release_4c4530(uint32_t, uint32_t);
extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t, uint32_t);
extern void g2_main_mspi_configure_finish_4c07d0(uint32_t);

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * UINT32_C(0x1000) + offset);
}

uint32_t g2_main_mspi_transfer_mode26_candidate(uint32_t controller,
                                                  const void *configuration)
{
    const volatile uint8_t *const bytes =
        (const volatile uint8_t *)(uintptr_t)controller;
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    if (bytes[8] == 0u)
        return 7u;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uint8_t serial = *(const uint8_t *)configuration;
    if ((module == 1u || module == 2u) &&
        serial >= 0x15u && serial <= 0x17u)
        return 5u;

    (void)g2_main_mspi_clock_route_4c0758(module, 0u, 0u, 0u);
    const uint8_t clock_class =
        (serial >= 3u && serial <= 0x17u && (serial & 1u)) ? 5u : 4u;
    volatile uint8_t *const saved_clock =
        (volatile uint8_t *)(uintptr_t)(controller + 0x8c9u);
    if (*saved_clock != clock_class) {
        uint32_t rc = g2_main_mspi_clock_release_4c4530(
            *saved_clock, (module + 0x10u) & 0xffu);
        if (rc != 0u) return rc;
        rc = g2_main_mspi_clock_acquire_4c44bc(
            clock_class, (module + 0x10u) & 0xffu);
        if (rc != 0u) return rc;
    }
    *saved_clock = clock_class;
    if (serial == 0u || serial > 0x17u)
        return 5u;
    const uint32_t clock_code = serial == 1u ? 7u :
                                (serial & 1u) ? 10u : 8u;
    (void)g2_main_mspi_clock_route_4c0758(
        module, 1u, 1u, clock_code);

    volatile uint32_t *const options = reg(module, 0x8cu);
    if (serial == 0x16u || serial == 0x17u)
        *options |= UINT32_C(0x40000000);
    else
        *options &= ~UINT32_C(0x40000000);

    uint32_t rate;
    if (serial <= 3u) rate = 0x200000u;
    else if (serial <= 5u) rate = 0x180000u;
    else if (serial <= 7u) rate = 0x100000u;
    else if (serial <= 9u) rate = 0xc0000u;
    else if (serial <= 11u) rate = 0x80000u;
    else if (serial <= 13u) rate = 0x60000u;
    else if (serial <= 15u) rate = 0x40000u;
    else if (serial <= 17u) rate = 0x30000u;
    else if (serial <= 19u) rate = 0x20000u;
    else rate = 0x10000u;
    volatile uint32_t *const format = reg(module, 0x84u);
    *format = (*format & UINT32_C(0xffc0ffff)) | rate;
    if (serial < 20u)
        *format &= ~UINT32_C(0x01c00000);
    else {
        *format |= UINT32_C(0x01000000);
        *format &= ~UINT32_C(0x00c00000);
    }

    const volatile uint32_t *const handle =
        (const volatile uint32_t *)(uintptr_t)controller;
    if (handle[6] != 0u) {
        *reg(module, 0x114u) = 0x20u;
        volatile uint32_t *const cq = reg(module, 0x118u);
        *cq = (*cq & ~0x1fu) | (serial <= 17u ? 8u : 12u);
        volatile uint32_t *const fifo = reg(module, 0x20u);
        *fifo = (*fifo & ~0x3f00u) | 0x1e00u;
        *cq = (*cq & ~0x1f00u) | 0x800u;
    }
    *(volatile uint8_t *)(uintptr_t)(controller + 12u) = serial;
    g2_main_mspi_configure_finish_4c07d0(controller);
    return 0u;
}
