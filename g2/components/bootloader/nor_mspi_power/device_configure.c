/* SPDX-License-Identifier: MIT
 * Apollo510 bootloader device configuration, reconstructed from locked
 * entries 0x424be4, 0x424120, and 0x424a18. The 24-byte bootloader record is
 * intentionally handled as byte offsets; it is not the public SDK C struct.
 */
#include "device_configure.h"
#include "../clock_manager/clock_manager.h"
#include <stdint.h>

#define MSPI0_BASE 0x40060000u
#define MODULE_STRIDE 0x1000u
#define HANDLE_MAGIC_MASK 0x01ffffffu
#define HANDLE_MAGIC 0x01bebebeu

extern uint32_t opencfw_bl_mspi_clockgen_control(uint32_t module,
    uint32_t enable, uint32_t configure, uint32_t source);

static volatile uint32_t *mspi_reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (MSPI0_BASE + module * MODULE_STRIDE + offset);
}

static uint32_t read_reg(uint32_t module, uint32_t offset)
{
    return *mspi_reg(module, offset);
}

static void write_reg(uint32_t module, uint32_t offset, uint32_t value)
{
    *mspi_reg(module, offset) = value;
}

/* Private helper 0x424120. Per-device serial/dual/quad/octal configuration
 * and timeout values are indexed by the bootloader's device enum byte. */
__attribute__((noinline))
void opencfw_bl_mspi_device_configure_private(uint32_t *handle)
{
    typedef struct {
        uint8_t devcfg;
        uint8_t set_cmdq;
        uint16_t xip_submode;
        uint8_t limit_kind;
    } device_mode_t;
    static const device_mode_t modes[26] = {
        {1, 1, 0x000, 0}, {2, 1, 0x000, 0}, {5, 0, 0x000, 0},
        {6, 0, 0x000, 0}, {9, 0, 0x000, 1}, {10, 0, 0x000, 0},
        {13,0, 0x000, 3}, {14,0, 0x000, 3}, {13,0, 0x000, 3},
        {14,0, 0x000, 3}, {17,0, 0x000, 2}, {14,0, 0x000, 3},
        {1, 0, 0x100, 0}, {2, 0, 0x100, 0},
        {1, 0, 0x300, 0}, {2, 0, 0x300, 0},
        {1, 0, 0x500, 1}, {2, 0, 0x500, 0},
        {1, 0, 0x700, 1}, {2, 0, 0x700, 1},
        {1, 0, 0x000, 0}, {2, 0, 0x000, 1},
        {1, 0, 0x900, 3}, {2, 0, 0x900, 0},
        {1, 0, 0xb00, 3}, {2, 0, 0xb00, 3},
    };
    const uint32_t module = handle[1];
    const uint8_t mode = ((volatile uint8_t *)handle)[10];
    if (mode >= sizeof(modes) / sizeof(modes[0]))
        return;
    const device_mode_t cfg = modes[mode];

    volatile uint32_t *const devcfg = mspi_reg(module, 0x84u);
    *devcfg = (*devcfg & 0xffffffe0u) | cfg.devcfg;
    if (cfg.set_cmdq)
        *devcfg |= 0x02000000u;
    else
        *devcfg &= 0xfdffffffu;

    volatile uint32_t *const xip = mspi_reg(module, 0x90u);
    *xip = (*xip & 0xfffff0ffu) | cfg.xip_submode;

    uint32_t limit;
    const uint8_t latency = ((volatile uint8_t *)handle)[9];
    switch (cfg.limit_kind) {
    case 1: limit = latency ? 0x8000001fu : 0x10fu; break;
    case 2: limit = latency ? 0x0007ffffu : 0x10fu; break;
    case 3: limit = 0x3ffu; break;
    default: limit = latency ? 0x80000013u : 0x103u; break;
    }
    write_reg(module, 0x44u, limit);
}

/* Private helper 0x424a18. Unmatched frequency codes leave the old delay. */
__attribute__((noinline))
void opencfw_bl_mspi_get_xip_off_min_delay(uint32_t *handle)
{
    const uint8_t frequency = ((volatile uint8_t *)handle)[0x0cu];
    if (frequency >= 6u && frequency <= 9u)
        handle[0x233u] = 8u;
    else if (frequency >= 10u && frequency <= 13u)
        handle[0x233u] = 4u;
    else if ((frequency >= 14u && frequency <= 15u) ||
             (frequency >= 18u && frequency <= 19u))
        handle[0x233u] = 2u;
    else if (frequency >= 20u && frequency <= 23u)
        handle[0x233u] = 1u;
}

static uint32_t sdr_frequency_word(uint8_t frequency, uint32_t *bits)
{
    if (frequency >= 1u && frequency <= 3u) *bits = 0x200000u;
    else if (frequency <= 5u && frequency >= 4u) *bits = 0x180000u;
    else if (frequency <= 7u && frequency >= 6u) *bits = 0x100000u;
    else if (frequency <= 9u && frequency >= 8u) *bits = 0x0c0000u;
    else if (frequency <= 11u && frequency >= 10u) *bits = 0x080000u;
    else if (frequency <= 13u && frequency >= 12u) *bits = 0x060000u;
    else if (frequency <= 15u && frequency >= 14u) *bits = 0x040000u;
    else if (frequency <= 17u && frequency >= 16u) *bits = 0x030000u;
    else if (frequency <= 19u && frequency >= 18u) *bits = 0x020000u;
    else if (frequency >= 20u && frequency <= 23u) *bits = 0x010000u;
    else return 5u;
    if (frequency >= 20u)
        *bits |= 0x01000000u;
    return 0u;
}

uint32_t opencfw_hal_mspi_device_configure(uint32_t handle_address,
                                           const void *config_pointer)
{
    uint32_t *const handle = (uint32_t *)(uintptr_t)handle_address;
    const uint8_t *const config = (const uint8_t *)config_pointer;
    if (handle == 0 || (handle[0] & HANDLE_MAGIC_MASK) != HANDLE_MAGIC)
        return 2u;
    if ((int8_t)handle[2] == 0)
        return 7u;

    const uint32_t module = handle[1];
    const uint8_t frequency = config[0x0b];
    const uint8_t ddr = config[0x11];
    if ((module == 1u || module == 2u) &&
        ((frequency >= 0x15u && frequency <= 0x17u) ||
         (config[8] >= 10u && config[8] <= 11u)))
        return 5u;

    opencfw_bl_mspi_clockgen_control(module, 0u, 0u, 0u);

    const uint8_t new_clock_class = ddr != 0u
        ? ((frequency == 0x15u || frequency == 0x17u) ? 5u : 4u)
        : ((frequency >= 3u && frequency <= 0x17u && (frequency & 1u))
            ? 5u : 4u);
    const uint8_t old_clock_class = ((volatile uint8_t *)handle)[0x8c9u];
    const uint8_t user = (uint8_t)(module + 0x10u);
    if (old_clock_class != new_clock_class) {
        uint32_t status = clock_release(old_clock_class, user);
        if (status != 0u)
            return status;
        status = clock_request(new_clock_class, user);
        if (status != 0u)
            return status;
    }
    ((volatile uint8_t *)handle)[0x8c9u] = new_clock_class;

    uint8_t clock_source;
    if (ddr == 0u) {
        if (frequency == 0u)
            return 5u;
        if (frequency == 1u) clock_source = 7u;
        else if (frequency >= 3u && frequency <= 0x17u && (frequency & 1u))
            clock_source = 10u;
        else if (frequency >= 2u && frequency <= 0x16u &&
                 !(frequency & 1u))
            clock_source = 8u;
        else
            return 5u;
    } else {
        if (frequency == 0x14u) clock_source = 7u;
        else if (frequency == 0x15u) clock_source = 9u;
        else if (frequency == 0x16u) clock_source = 8u;
        else if (frequency == 0x17u) clock_source = 10u;
        else return 5u;
    }
    opencfw_bl_mspi_clockgen_control(module, 1u, 1u, clock_source);

    volatile uint32_t *const c1 = mspi_reg(module, 0x8cu);
    if (ddr == 0u && (frequency == 0x16u || frequency == 0x17u))
        *c1 |= 0x40000000u;
    else
        *c1 &= 0xbfffffffu;

    uint32_t config_word = ((uint32_t)(config[1] & 3u) << 5) |
                           ((uint32_t)(config[2] & 1u) << 7) |
                           ((uint32_t)(config[0] & 0x3fu) << 8);
    if (config[10] == 2u) config_word |= 0x4000u;
    else if (config[10] == 1u) config_word |= 0x8000u;
    else if (config[10] == 3u) config_word |= 0xc000u;
    if (ddr == 0u) {
        uint32_t frequency_bits = 0;
        const uint32_t status = sdr_frequency_word(frequency,
                                                    &frequency_bits);
        if (status != 0u)
            return status;
        config_word |= frequency_bits;
    }
    config_word |= (uint32_t)config[9] << 26;
    write_reg(module, 0x84u, config_word);

    volatile uint32_t *const c0 = mspi_reg(module, 0x88u);
    if (ddr == 0u)
        *c0 = (*c0 & ~1u) | (config[0x10] != 0u);
    else {
        *c0 |= 1u;
        *c1 |= 0x80000000u;
    }
    *c1 = (*c1 & 0xfff9ffffu) | ((uint32_t)(config[0x12] & 3u) << 17);

    volatile uint32_t *const enable = mspi_reg(module, 0x30u);
    *enable &= ~1u;
    uint32_t xip = 0xfc001f03u & read_reg(module, 0x90u);
    xip |= 0x0cu | ((uint32_t)((volatile uint8_t *)handle)[0x0du] << 4);
    if (config[0x0f] != 0u)
        xip |= ((uint32_t)(config[0] & 0x3fu) << 14) | 0x20u;
    if (config[0x0d] != 0u) xip |= 0x40u;
    if (config[0x0e] != 0u) xip |= 0x80u;
    xip |= ((uint32_t)config[0x0c] << 13) |
           ((uint32_t)(config[9] & 0x3fu) << 20);
    write_reg(module, 0x90u, xip);

    write_reg(module, 0x94u,
        (uint32_t)*(const uint16_t *)(const void *)(config + 4u) |
        ((uint32_t)*(const uint16_t *)(const void *)(config + 6u) << 16));
    write_reg(module, 0x98u,
        (*(const uint16_t *)(const void *)(config + 0x14u) & 0xfffu) |
        ((uint32_t)(config[0x16] & 0x0fu) << 12));
    *enable = (*enable & 0xffffff0fu) | 0x70u;
    ((volatile uint8_t *)handle)[0x0du] = 0u;

    if (handle[6] != 0u) {
        write_reg(module, 0x114u, 0x20u);
        if (frequency >= 1u && frequency <= 17u) {
            uint32_t reg = read_reg(module, 0x118u);
            write_reg(module, 0x118u, (reg & 0xffffffe0u) | 8u);
            reg = read_reg(module, 0x20u);
            write_reg(module, 0x20u, (reg & 0xffffc0ffu) | 0x1e00u);
            reg = read_reg(module, 0x118u);
            write_reg(module, 0x118u, (reg & 0xffffe0ffu) | 0x800u);
        } else if (frequency >= 18u && frequency <= 23u) {
            uint32_t reg = read_reg(module, 0x118u);
            write_reg(module, 0x118u, (reg & 0xffffffe0u) | 0x0cu);
            reg = read_reg(module, 0x20u);
            write_reg(module, 0x20u, (reg & 0xffffc0ffu) | 0x1e00u);
            reg = read_reg(module, 0x118u);
            write_reg(module, 0x118u, (reg & 0xffffe0ffu) | 0x800u);
        } else {
            return 5u;
        }
    }

    ((volatile uint8_t *)handle)[10] = config[8];
    opencfw_bl_mspi_device_configure_private(handle);
    ((volatile uint8_t *)handle)[0x0du] = 0u;
    handle[3] = frequency;
    handle[4] = 10000u;
    opencfw_bl_mspi_get_xip_off_min_delay(handle);
    return 0u;
}
