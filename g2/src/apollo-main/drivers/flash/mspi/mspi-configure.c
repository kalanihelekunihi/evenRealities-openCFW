/* SPDX-License-Identifier: MIT
 * Main 0x4c099c: MSPI serial configuration and register programming.
 * The native configuration record is byte-packed and the controller handle
 * is a firmware SRAM address, so keep byte offsets explicit.
 */
#include <stdint.h>

extern void g2_main_mspi_clock_route_4c0758(uint32_t, uint32_t,
                                               uint32_t, uint32_t);
extern uint32_t g2_main_mspi_clock_release_4c4530(uint32_t, uint32_t);
extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t, uint32_t);
extern void g2_main_mspi_configure_aux_4bfed6(uint32_t);
extern void g2_main_mspi_configure_finish_4c07d0(uint32_t);

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * UINT32_C(0x1000) + offset);
}

static uint32_t half(const uint8_t *bytes)
{
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8);
}

uint32_t g2_norflash_configure_mspi_4c099c(uint32_t controller,
                                             const void *configuration)
{
    volatile uint32_t *const handle =
        (volatile uint32_t *)(uintptr_t)controller;
    const uint8_t *const cfg = (const uint8_t *)configuration;
    if (controller == 0u ||
        (handle[0] & UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    if (*(volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;

    const uint32_t module = handle[1];
    if ((module == 1u || module == 2u) &&
        ((cfg[11] >= 0x15u && cfg[11] <= 0x17u) ||
         (cfg[8] >= 10u && cfg[8] <= 11u)))
        return 5u;

    g2_main_mspi_clock_route_4c0758(module, 0u, 0u, 0u);
    const uint8_t serial = cfg[11];
    uint8_t clock_class;
    uint32_t serial_code;
    if (cfg[17] == 0u) {
        clock_class = (serial >= 3u && serial <= 0x17u &&
                       (serial & 1u)) ? 5u : 4u;
        serial_code = serial == 1u ? 7u :
                      (serial >= 3u && (serial & 1u)) ? 10u : 8u;
    } else {
        clock_class = (serial == 0x15u || serial == 0x17u) ? 5u : 4u;
        serial_code = serial == 0x14u ? 7u :
                      serial == 0x15u ? 9u :
                      serial == 0x16u ? 8u : 10u;
    }
    volatile uint8_t *const saved_clock =
        (volatile uint8_t *)(uintptr_t)(controller + 0x8c9u);
    if (*saved_clock != clock_class) {
        uint32_t rc = g2_main_mspi_clock_release_4c4530(
            *saved_clock, (module + 0x10u) & 0xffu);
        if (rc != 0u)
            return rc;
        rc = g2_main_mspi_clock_acquire_4c44bc(
            clock_class, (module + 0x10u) & 0xffu);
        if (rc != 0u)
            return rc;
    }
    *saved_clock = clock_class;
    if ((cfg[17] == 0u && (serial == 0u || serial > 0x17u)) ||
        (cfg[17] != 0u && (serial < 0x14u || serial > 0x17u)))
        return 5u;
    g2_main_mspi_clock_route_4c0758(module, 1u, 1u, serial_code);

    volatile uint32_t *const mode = reg(module, 0x8cu);
    if (cfg[17] == 0u && (serial == 0x16u || serial == 0x17u))
        *mode |= UINT32_C(0x40000000);
    else
        *mode &= ~UINT32_C(0x40000000);

    uint32_t format = ((uint32_t)cfg[1] & 3u) << 5 |
                      ((uint32_t)cfg[2] & 1u) << 7 |
                      ((uint32_t)cfg[0] & 0x3fu) << 8;
    if (cfg[10] == 1u) format |= 0x8000u;
    else if (cfg[10] == 2u) format |= 0x4000u;
    else if (cfg[10] == 3u) format |= 0xc000u;
    if (cfg[17] == 0u) {
        uint32_t rate;
        if (serial >= 1u && serial <= 3u) rate = 0x200000u;
        else if (serial <= 5u) rate = 0x180000u;
        else if (serial <= 7u) rate = 0x100000u;
        else if (serial <= 9u) rate = 0xc0000u;
        else if (serial <= 11u) rate = 0x80000u;
        else if (serial <= 13u) rate = 0x60000u;
        else if (serial <= 15u) rate = 0x40000u;
        else if (serial <= 17u) rate = 0x30000u;
        else if (serial <= 19u) rate = 0x20000u;
        else if (serial <= 23u) rate = 0x10000u;
        else return 5u;
        format |= rate;
        if (serial >= 20u)
            format |= 0x1000000u;
    }
    *reg(module, 0x84u) = format | ((uint32_t)cfg[9] << 26);
    volatile uint32_t *const control = reg(module, 0x88u);
    if (cfg[17] == 0u)
        *control = (*control & ~1u) | (cfg[16] != 0u);
    else {
        *control |= 1u;
        *mode |= UINT32_C(0x80000000);
    }
    *mode = (*mode & ~UINT32_C(0x00060000)) |
            (((uint32_t)cfg[18] & 3u) << 17);
    volatile uint32_t *const active = reg(module, 0x30u);
    *active &= ~1u;

    uint32_t options = (*reg(module, 0x90u) & UINT32_C(0xfc001f03)) |
                       0xcu |
                       ((uint32_t)*(volatile uint8_t *)(uintptr_t)
                        (controller + 13u) << 4);
    if (cfg[15] != 0u)
        options |= (((uint32_t)cfg[0] & 0x3fu) << 14) | 0x20u;
    if (cfg[13] != 0u) options |= 0x40u;
    if (cfg[14] != 0u) options |= 0x80u;
    *reg(module, 0x90u) = options |
                          ((uint32_t)cfg[12] << 13) |
                          (((uint32_t)cfg[9] & 0x3fu) << 20);
    *reg(module, 0x94u) = (half(cfg + 4u) << 16) | half(cfg + 6u);
    *reg(module, 0x98u) = (half(cfg + 20u) & 0xfffu) |
                          (((uint32_t)cfg[22] & 0xfu) << 12);
    *active = (*active & ~0xf0u) | 0x70u;
    *(volatile uint8_t *)(uintptr_t)(controller + 13u) = 0u;

    if (handle[6] != 0u) {
        *reg(module, 0x114u) = 0x20u;
        if (serial == 0u || serial > 0x17u)
            return 5u;
        volatile uint32_t *const cq = reg(module, 0x118u);
        *cq = (*cq & ~0x1fu) | (serial <= 0x11u ? 8u : 12u);
        volatile uint32_t *const fifo = reg(module, 0x20u);
        *fifo = (*fifo & ~0x3f00u) | 0x1e00u;
        *cq = (*cq & ~0x1f00u) | 0x800u;
    }
    *(volatile uint8_t *)(uintptr_t)(controller + 10u) = cfg[8];
    g2_main_mspi_configure_aux_4bfed6(controller);
    *(volatile uint8_t *)(uintptr_t)(controller + 13u) = 0u;
    *(volatile uint8_t *)(uintptr_t)(controller + 12u) = serial;
    handle[4] = 10000u;
    g2_main_mspi_configure_finish_4c07d0(controller);
    return 0u;
}
